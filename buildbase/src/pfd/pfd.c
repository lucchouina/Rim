#include <syslog.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdarg.h>
#include <string.h>
#include <getopt.h>
#include <sys/select.h>
#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <stdio.h>
#include <signal.h>
#include <stdlib.h>
#include <netinet/ip.h>
#include <pthread.h>
#include <netinet/ip_icmp.h>
#include <netdb.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <netdb.h>
#include <sys/ioctl.h>
#include <linux/if.h>
#include <linux/sockios.h>
#include <dlfcn.h>

/*
    This program provides for simple port forwarding.
    
    In short:
    
    It is used to setup port forwarding to/from tcp/sockets or 
    unix/sockets.
    
    NAT , ssh or socat do not work properly for what we wan to do. 
    They do not support one critical requirement which is to not 
    break the connection when the remote end goes away, i.e. when the unix
    socket file is removed (which is what vmWare does when one powers down 
    or resets a VM) or when the terminal server goes away etc...
    
    First implementation : Luc 11/03/2006
    
*/
#define PFRS_FNAME  "pfrs"
#define PFD_MAXSOCK 10000  // special fd value to sheild against setupEnd() calls on lfd
#define CLIENT_INT "eth1"
static char *confDir=0;
static char *clientInt=CLIENT_INT;
static int isClient=0, redoConf=0;
static short ctlPort=12012;
static char *nic=0, *server=0;
static char *confFile(char *fname)
{
static char buf[200];
    snprintf(buf, sizeof buf, "%s/%s", confDir, fname);
    return buf;
}

/*
    Format is:
    source destination whwre source and destination have the following format:
    [host]:proto:port:flags
    
    By default 'host' is localhost if outbound and 'INADDR_ANY' if inbound.
    
    Examples :
    
    :unix:/tmp/socket:flags   : listen or forward to a local Unix socket file
    
    flags can be a comma separated list of:
    
    telnet      :   handle initial "char" mode handshake and gobble up 
                    all 0xff sequences.
    multi       :   Accept multiple connection requests to this port.
*/

static int dbglvl=1; // start at 1 so that we send to termnal untill syslog is up
static int curline=0;

static int is_cnum(char *name)
{
    if(!strncmp(name, "cIp", 3)) {
    
        int num=atoi(name+3);
        return num;
    
    }
    return -1;
}


void dbg(int level, int doerr, int die, char *fmt, ...)
{
va_list ap;
int docr=0;
char myfmt[1024];
char msg[1024], *p=msg;

    strcpy(myfmt, fmt);
    if(level>dbglvl) return;
    // remove trailing CR
    if(myfmt[strlen(myfmt)-1]=='\n') {
        myfmt[strlen(myfmt)-1]='\0';
        docr=1;
    }
    va_start(ap, fmt);
    p += vsnprintf(p, 1024-(p-msg), myfmt, ap);
    if(doerr) p += snprintf(p, 1024-(p-msg), " : %s", strerror(errno));
    if(docr || doerr) *p++='\n';
    *p='\0';
    if(dbglvl) fprintf(stderr, "%s", msg);
    else syslog(LOG_ERR, "%s", msg);
    va_end(ap);
    //free(myfmt);
    if(die) 
        exit(1);
}

void mkalldirs(char *path)
{
char *p=path+1;

    while(*p) {
        if(*p=='/') {
        
            *p='\0';
            if(mkdir(path, 0755) && errno != EEXIST)
                dbg(0,0,1, "Could not create diretory '%s'\n", path);
            *p='/';
        }
        p++;
    }
}

#define POLL_INTERVAL 1 // interval for polling for dangling UNIX ends

// types of end points
#define END_TYPE_TCP        1
#define END_TYPE_UDP        2
#define END_TYPE_UNIX       3
#define END_TYPE_DEVICE     4

// end point struct
typedef struct end_s end_t;
struct end_s {

    int type;    // end point type (TCP/UDP/UnixSocket/Device)
    int num;     // 0: sin_addr is good. >0: is resolved by client connections
    union {
        struct sockaddr_un  un;
        struct sockaddr_in  in;
        char                *devname;
    } addr;
    int fd;     // listen socket for INET or file descriptor for UNIX or DEV
};

#define FR_FLAG_TELNET      0x00000001
#define FR_FLAG_MULTI       0x00000002
#define FR_FLAG_CRLF        0x00000004
#define FR_FLAG_NAME        0x00000008
#define FR_FLAG_COORD       0x00000010

#define FR_FLAG_FOUND       0x80000000 // for update purpose

// one connection 
typedef struct con_s con_t;
struct con_s {

    time_t  created;        // time created
    time_t  last;           // time of last inbound activity
    int     infd;           // incoming socket
    void    *indata;        // private addr for in fd
    int     outfd;          // outgoing socket
    void    *outdata;        // private addr for out fd
    con_t   *next;
}; 
    

// forward rule struct 
typedef struct fr_s fr_t;
struct fr_s {

    int flags;
    char    *name;              // name of the service associated
    int     mine;               // do I own this FR ?
    int     cnum, snum, nnum;   // coordinates (chassis,slot,node)
    int     lfd;                // listen inbound fd
    int     cfd;                // common fd for UNIX connections
    int     ref;                // ref count to the above
    end_t   in;
    end_t   out;
    con_t   *clist;             // list of current connections
    struct fr_s * next;
    time_t  last;               // last outbound activity
    
};

typedef struct  {

    int key;
    char *name;

} klist_t;
static klist_t klist[] = {

    {0,                     ""          },     // invalid
    {FR_FLAG_MULTI,         "multi"     },
    {FR_FLAG_TELNET,        "telnet"    },
    {FR_FLAG_COORD,         "coord"    },
    {FR_FLAG_NAME,          "name"    },
};
#define NFLGS (sizeof klist/sizeof klist[0])

static int getkeybyname(char *kname, char **value)
{
uint32_t i;
char *equal;

    if((equal=index(kname, '='))) {
        *equal='\0';
        *value=equal+1;
    }
    for(i=1;i<sizeof(klist)/sizeof(klist[0]);i++) {
    
        if(!strcasecmp(klist[i].name, kname)) {
            if(equal) *equal='=';
            return klist[i].key;
        }
    }
    dbg(0, 0, 1, "Invalid flag specified '%s' @ line %d", kname, curline);
    return 0;
}

static int parseFlags(char *fstr, fr_t *fr)
{
char *s=strdup(fstr), *tok, *value;   
    fr->flags=0;
    tok=strtok(s, ",\n");
    while(tok) {
        int key=getkeybyname(tok, &value);
        switch(key) {
        
            case FR_FLAG_COORD : {
            
                // we are given a set of coordinates cnum:snum:nnum
                if(sscanf(value, "%d:%d:%d", &fr->cnum,&fr->snum,&fr->nnum) != 3) 
                    dbg(0,0,1,"Invalid coordinates '%s'\n", value);
            
            }
            break;
            case FR_FLAG_NAME: {
            
                fr->name=strdup(value);
            
            }
            break;
            case 0: return 0;
            default: {
            
                fr->flags |= key;
            }
        
        }
        tok=strtok(0, ",\n");
    }
    return 1;
}


static fr_t *frlist=0;

static int endSame(end_t *end1, end_t *end2)
{
    if(end1->type == end2->type) {
        if(end1->type==END_TYPE_UNIX) {
            if(strcmp(end1->addr.un.sun_path, end2->addr.un.sun_path)) return 0;
        }
        else {
            if(memcmp(
                    &end1->addr.in.sin_addr.s_addr, 
                    &end2->addr.in.sin_addr.s_addr, 
                    sizeof(end2->addr.in.sin_addr.s_addr))) return 0;
            if(end1->addr.in.sin_port != end2->addr.in.sin_port) return 0;
        }
        return 1;
    }
    return 0;
}

static int frSame(fr_t *fr1, fr_t *fr2)
{
    if(!endSame(&fr1->in, &fr2->in)) return 0;
    if(!endSame(&fr1->out, &fr2->out)) return 0;
    if(fr1->flags != fr2->flags) return 0;
    return 1;
}

static void resetFoundFlags()
{
fr_t *fr=frlist;

    while(fr) {
    
        fr->flags &= ~FR_FLAG_FOUND;
        fr=fr->next;
    }
}

static char *addrStr(end_t *e)
{
static char cnumstr[40];
    if(!e->num) return inet_ntoa(e->addr.in.sin_addr);
    else {
        sprintf(cnumstr, "chassis[%d][%s]", e->num, inet_ntoa(e->addr.in.sin_addr));
        return cnumstr;
    }

}

static char *endStr(end_t *e, char *buf, int l)
{
    switch(e->type) {
        case END_TYPE_UNIX:
        snprintf(buf, l, "%s:%s:%s"
        , "localhost","unix", e->addr.un.sun_path);
        break;
        case END_TYPE_TCP: case END_TYPE_UDP:
        snprintf(buf, l, "%s:%s:%d"
        , addrStr(e)
        , e->type==END_TYPE_TCP?"tcp":"udp"
        , ntohs(e->addr.in.sin_port));
        break;
    }        
    return buf;
}

static char *flagsStr(fr_t *fr, char *buf, int l)
{
    uint32_t i, pos, one=0;
    buf[0]='\0';
    for(i=0, pos=0;i<NFLGS;i++) {
        if(fr->flags&klist[i].key) {
            if(one) pos+=snprintf(buf+pos, l-pos, ",");
            one++;
            pos+=snprintf(buf+pos, l-pos, klist[i].name);
        }
    }
    if(fr->cnum) pos+=snprintf(buf+pos, l-pos, " coord=%d:%d:%d", fr->cnum, fr->snum, fr->nnum);
    if(fr->name) pos+=snprintf(buf+pos, l-pos, " name=%s", fr->name);
    return buf;
}

static void prpfr(fr_t *f)
{
char b1[40], b2[40], b3[40];

    dbg(1,0,0,"From: %-20s To: %-40s flags: %-30s\n"
        , endStr(&f->in, b1, sizeof b1)
        , endStr(&f->out, b2, sizeof b2)
        , flagsStr(f, b3, sizeof b3));    
}

static void closeFr(fr_t* fr)
{
con_t *c=fr->clist;

    dbg(1,0,0,"   Closing fr [0x%08x] fd %d cfd %d\n", fr, fr->lfd, fr->cfd);
    prpfr(fr);
    if(fr->lfd>=0) close(fr->lfd);
    if(fr->cfd>=0) close(fr->cfd);
    while(c) {
    
        con_t *next=c->next;
        if(c->infd>=0) {
            dbg(1,0,0,"   Closing connection infd %d\n", c->infd);
            close(c->infd);
        }
        if(c->outfd>=0 && c->outfd!=fr->cfd) {
            dbg(1,0,0,"   Closing connection outfd %d\n", c->outfd);
            close(c->outfd);
        }
        free(c);
        c=next;
    }
    if(fr->lfd>=0) close(fr->lfd);
    free(fr);
}

static int findFr(fr_t *newfr)
{
fr_t *fr=frlist;

    while(fr) {
    
        if(frSame(newfr, fr)) {
            fr->flags |= FR_FLAG_FOUND;
            return 1;
        }
        fr=fr->next;
    }
    return 0;
}

static fr_t *newFr()
{
fr_t *f=(fr_t*)calloc(sizeof *f, 1);

    f->lfd=-1;
    return f;
}

static con_t *newCon()
{
con_t *c=(con_t*)calloc(sizeof *c, 1);
    c->infd=-1;
    c->outfd=-1;
    return c;
}

// setup an end point
static void setupEnd(end_t *e, int *cfd, int *ref, int *fd, con_t **cpp, int dolisten)
{
    if(e->type==END_TYPE_TCP) {
        int sock, on=1;
        if((sock=socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)) >= 0) {
            setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &on, sizeof on);
            fcntl(sock, F_SETFL, O_NONBLOCK);
            if(dolisten) {
                if(bind(sock, (struct sockaddr *) &e->addr.in, sizeof(e->addr.in)) >= 0) {
                    if(listen(sock,64)) dbg(0,1,0, "TCP listen");
                    *fd=sock;
                    return;
                }
                else dbg(0,1,0,"TCP bind");
            }
            else {

                if(connect(sock, (struct sockaddr *) &e->addr.in, sizeof(e->addr.in)) &&
                    errno != EINPROGRESS){
                    dbg (0,1,0,"TCP connect");
                    
                } else {

                    *fd=sock;
                    return;
                }
            }   
            close(sock); 
        }
        else dbg(0,1,1,"TCP socket");
    }
    else if(e->type==END_TYPE_UDP) {
    
        int sock, on=1;
        dbg (1,0,0,"UDP setup end 0x%p\n", e);
        //
        //
        // In the case of UDP, we create one connection and leave it
        // at that. Set lfd to PFD_MAXSOCK and assign the connections in and out
        // fd to the bounded address sockets.
        //
        if((sock=socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) >= 0) {
            setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &on, sizeof on);
            if(dolisten) {
                if(bind(sock, (struct sockaddr *) &e->addr.in, sizeof(e->addr.in)) >= 0) {
                    con_t *c=newCon();
                    if(*cpp) dbg(0,0,1,"Found another UDP connection!\n"); 
                    c->infd=sock;
                    c->next=0;
                    *cpp=c;
                    *fd=PFD_MAXSOCK;
                }
                else dbg(0,1,0,"UDP bind");
            }
            else {
            
                if(connect(sock, (struct sockaddr *) &e->addr.in, sizeof(e->addr.in)) >= 0) {
                    *fd=sock;
                    (*cpp)->outdata=&e->addr.in;
                }
                else dbg(0,1,0,"UDP listen");
            }
            
            return;
            close(sock); 
        }
        else dbg(0,1,1,"UDP socket");
    
    }
    else if(e->type==END_TYPE_UNIX) {
    
        if(!*ref) {
            int sock;
            // make sure the directory itself exists
            // this helps making more resilient in that vmware does not create the
            // Directories associated with a socket file.
            //
            mkalldirs(e->addr.un.sun_path);
            if((sock=socket(AF_UNIX, SOCK_STREAM, 0)) >= 0) {
                if(dolisten) {
                    if(bind(sock, (struct sockaddr *) &e->addr.un, sizeof(e->addr.un)) >= 0) {
                        if(listen(sock,64)) dbg(0,1,0, "Unix listen");
                        *fd=sock;
                        return;
                    }
                    else dbg(0,1,0,"Unix bind");
                }
                else {

                    if(connect(sock, (struct sockaddr *) &e->addr.un, sizeof(e->addr.un)))
                        dbg (0,1,0,"Unix connect");
                    else {

                        *fd=sock;
                        *cfd=sock;
                        *ref+=1;
                        return;
                    }
                }
            }
            else dbg(0,1,1,"unix socket");
            close(sock); 
        }
        // add a reference to the UNIX socket (shared consoles)
        else {
        
            if(*cfd<0) dbg(0,0,1,"Found cfd %d on ref %d\n", *cfd, *ref);
            *fd=*cfd;
            *ref+=1;
        }
    }
}
static void closeCon(fr_t *f, con_t *c)
{
con_t *cl=f->clist, **last=&f->clist;

    while(cl) {
    
        if(c==cl) break;
        last=&cl->next;
        cl=cl->next;
    }
    if(!cl) dbg(0,0,1,"Connection not found!\n");
    dbg(1,0,0,"closing Connection %08x\n", c);
    prpfr(f);
   *last=cl->next;
    if(cl->infd>=0) {
        dbg(1,0,0,"Closing connection IN fd %d\n", cl->infd);
        close(cl->infd);
    }
    if(cl->outfd>=0) {
        if(cl->outfd==f->cfd) {
        
            dbg(1,0,0,"Found common fd for close [%d][ref=%d]\n", f->cfd, f->ref);
            f->ref--;
            if(!f->ref) {
                close(f->cfd);
                f->cfd=-1;
            }
        }
        else close(cl->outfd);
    }
    free(cl);
}

static int clientLookup(int cnum)
{
    return -1;
}

//
// check if any of the listen or output targets need to be setu
static void frPollSocks()
{
fr_t *f=frlist;

    while(f) {
    
        con_t *c=f->clist;
    
        if(f->mine && f->lfd==-1) setupEnd(&f->in, &f->cfd, &f->ref, &f->lfd, &f->clist, 1);
        // check the connections 
        while(c) {
            // only UNIX inbound can be left dangling
            if(c->infd==-1) {
                if(f->in.type!=END_TYPE_UNIX) dbg(0,0,1,"Found connection with dangling inbound socket!\n");
                setupEnd(&f->in, &f->cfd, &f->ref, &c->infd, &f->clist, 0);
            }
            if(c->outfd==-1) {
                // here we check if the end point is defined dynamically through client connections
                // and if the client has registered.
                if(f->out.num) {
                    // try to refresh the address through the client registration table
                    f->out.addr.in.sin_addr.s_addr=clientLookup(f->out.num);
                }
                setupEnd(&f->out, &f->cfd, &f->ref, &c->outfd, &f->clist, 0);
                // a failure of a TCP fr outbound fails the entire thing
                if(c->outfd==-1 && f->out.type!=END_TYPE_UNIX) {
                    if(c->infd>0) {
                        #define MSG "\n**********************************\n   Is target up and running PFD??\n**********************************\n"
                        write(c->infd, strerror(errno), strlen(strerror(errno)));
                        write(c->infd, MSG, sizeof MSG-1);
                        sleep(5);
                    }
                    closeCon(f, c);
                }
            }
            c=c->next;
        }
        f=f->next;
    }
}

#define setfd(fd) if(fd >= 0 && fd < PFD_MAXSOCK) { if(fd>maxfd) maxfd=fd; FD_SET(fd, fdset); }
static int frSetFds(fd_set *fdset, int maxfd)
{
fr_t *f=frlist;

    while(f) {
    
        con_t *c=f->clist;
    
        setfd(f->lfd);
        // check the connections 
        while(c) {
            setfd(c->infd);
            setfd(c->outfd);
            c=c->next;
        }
        f=f->next;
    }
    return maxfd;
}

// maximum number of bytes transfered per process loop
// will make the process fare for all.
#define MAXTRBYTES      1000
#include <arpa/telnet.h>
static char *xlateTelnet(int in, char *buf, int *nbytes)
{
     // not supportted for now
     return buf;
}

static char *xlateCrlf(int in, char *buf, int *nbytes)
{
     // not supportted for now
     return buf;
}

// translate based on flags
static char *xlatebytes(int in, char *inb, int nin, int *nout, int flags)
{
char *curbuf;

    // We move the buffer through a series of translations
    curbuf=inb;
    *nout=nin;
    // short cut for no processing
    if(!(flags & (FR_FLAG_TELNET+FR_FLAG_CRLF))) {
        
        return inb;
    }
    if(flags & FR_FLAG_TELNET) curbuf=xlateTelnet(in, curbuf, nout);
    if(flags & FR_FLAG_CRLF)   curbuf=xlateCrlf(in, curbuf, nout);
    return curbuf;
}

// transfer the data from one file descriptor to another
// Possibly do some processing based on FR flags
// 
static int transfer(int *in, void **indata, int **out, void **outdatas, int flags, int typeIn, int typeOut)
{
char buf[MAXTRBYTES], *tbuf;
int nin,nout=0;
    
    // with UDP we need to connect the socket to the clients address
    if(typeIn==END_TYPE_UDP) {
        socklen_t socklen = sizeof(struct sockaddr_in);
        struct sockaddr_in *sock_client=malloc(sizeof *sock_client);
        if ((nin=recvfrom(*in, buf, MAXTRBYTES, 0,(struct sockaddr *) sock_client, &socklen)) > 0) {

            buf[nin]='\0';
            dbg (2,0,0,"Received %d bytes from %s.[%s]\n", nin, inet_ntoa(sock_client->sin_addr), buf);
            //
            // record this incoming client, we will send out side read data to it.
            *indata=sock_client;
        }
    } else nin=read(*in, buf, MAXTRBYTES);
    
    if(nin > 0) {
        int n=0;
        tbuf=xlatebytes(*in, buf, nin, &nout, flags);
        while(n!=nout){
            int now=0;
            int i=0;
            //
            // we may have to send the new data to many listeners.
            //
            while(out[i]) {
            
                dbg(5,0,0, "out[%d]=0x%08x outfd=%d\n", i, out[i], *out[i]);
                
                if(typeOut==END_TYPE_UDP) {
                    now=sendto(*out[i], tbuf+n, nout-n, 0, (struct sockaddr *)outdatas[i], sizeof(struct sockaddr));
                } else {
                    now=write(*out[i], tbuf+n, nout-n);
                }
                if(now<0) {
                    dbg(1,1,0,"Write error closing OUT fd %d\n", *out[i]);
                    close(*out[i]);
                    *out[i]=-1;
                    now=nout-n;
                }
                i++;
            }
            n+=now;
        }
        if(tbuf != buf) free(tbuf); 
        return 1;
    }
    dbg(1,1,0,"Read error, closing IN fd %d\n", nin, *in);
    close(*in);
    *in=-1;
    return 0;
} 

static void frProcessFds(fd_set *fdset)
{
fr_t *f=frlist;

    while(f) {
    
        con_t *c;
    
        if(f->lfd > 0 && f->lfd < PFD_MAXSOCK && FD_ISSET(f->lfd, fdset)) {
            struct sockaddr_in cliAddr;
            int sock;
            socklen_t cliLen;
            cliLen = sizeof(cliAddr);

            // new incoming connection
            if((sock=accept(f->lfd,(struct sockaddr *) &cliAddr, &cliLen)) < 0) {
                
                dbg(0,1,0,"Failed to accept incoming console connection\n");
                
            }
            else {
            
                // open the outgoing end
                
                // check if we sholuld open more then one
                if(f->clist && !(f->flags & FR_FLAG_MULTI)) {
                
                    dbg(0,0,0, "Connection busy. Dropping incoming request.\n");
                    close(sock);
                    
                }else 
                {
                    
                    con_t *c=newCon();
                    dbg(1,0,0, "New connection on fd %d\n", sock);
                    c->infd=sock;
                    c->next=f->clist;
                    f->clist=c;
                    frPollSocks();
                }
            }
        }
        {
            // check the connections 
            c=f->clist;
            while(c) {
                con_t *next=c->next;
                int nfd=0, *fds[10];
                void *datas[10];
                
                if(c->infd>=0 && c->infd < PFD_MAXSOCK && FD_ISSET(c->infd, fdset)) {

                    // read from input fd and write on output fd
                    dbg(5,0,0,"Input activity on fd %d\n", c->infd);
                    //sleep(1);
                    nfd=1;
                    fds[0]=&c->outfd;
                    fds[1]=0;
                    datas[0]=c->outdata;
                    transfer(&c->infd, &c->indata, fds, datas, f->flags, f->in.type, f->out.type);

                    if(c->infd < 0) {
                        if(f->in.type != END_TYPE_UNIX) closeCon(f, c);
                    }else{
                        FD_CLR(c->infd, fdset);
                    }    
                }
                if(c->outfd>=0 && c->outfd < PFD_MAXSOCK && FD_ISSET(c->outfd, fdset)) {
                
                    // if this is UNIX then duplicate output to all listeners.
                    if(f->out.type == END_TYPE_UNIX) {
                    
                        con_t *uc=c;
                        while(uc) {
                        
                            fds[nfd++]=&uc->infd;
                            uc=uc->next;
                        }
                        fds[nfd++]=0;
                    }
                    else {
                    
                        nfd=1;
                        fds[0]=&c->infd;
                        fds[1]=0;
                        datas[0]=c->indata;
                    }

                    // read from output fd and write on input fd
                    transfer(&c->outfd, &c->outdata, fds, datas, f->flags, f->out.type, f->in.type);

                    if(c->outfd < 0) {
                        if(f->out.type != END_TYPE_UNIX) closeCon(f, c);
                        else {
                            con_t *uc=f->clist;
                            if(f->ref) f->ref--;
                            else dbg(0,0,1,"Found ref == 0 while cleaning unix outfd\n");
                            dbg(1,0,0,"Closing all ref to fd %d for Unix\n", f->cfd);
                            while(uc) {

                                if(uc != c && uc->outfd==f->cfd) {
                                    if(f->ref) f->ref--;
                                    else dbg(0,0,1,"Found ref == 0 while cleaning unix outfd\n");

                                    uc->outfd=-1;
                                }
                                uc=uc->next;
                            }
                            f->cfd=-1;
                        }
                    }else{
                        FD_CLR(c->outfd, fdset);
                    }                    
                }


                c=next;
            }
        }
        f=f->next;
     }
}

static int getNum(uint8_t *x, uint8_t **xp)
{
int v=0;

    while(*x && *x >= '0' && *x <= '9') { v=v*10+(*x-'0'); x++; }
    *xp=x;
    return v;
}

static int eval(uint8_t *x, uint8_t **xp, int level)
{
int v=0;
    while(*x) {
        if(*x>='0' && *x<='9') v=getNum(x, &x);
        else switch(*x) {
    
            case ')': { 
                if(!level) printf("One too many ')'\n");
                *xp=x; 
                return v; 
            }
            case '(': {
                v=eval(x+1, &x, level+1);
                if(*x != ')') printf("Missing ')'\n");
                else x++;
            }
            break;
            case '+': v=v+eval(x+1, &x, level); break;
            case '-': v=v-eval(x+1, &x, level); break;
            case '*': v=v*eval(x+1, &x, level); break;
            default: printf("Invalid expression '%s'\n", x);
        }
    }
    *xp=x;
    return v;
}

static int parseOne(char *line, end_t *end)
{
char *p, *l=strdup(line), *host, *type, *li=l, *addr;
//uint8_t *addr;

    dbg(2,0,0,"One [%s]\n", line);
    // host
    if((p=index(l, ':'))) {

        host=l;
        *p='\0';
        l=p+1;

        // addr type
        if((p=index(l, ':'))) {

            type=l;
            *p='\0';
            l=p+1;

            // port or unix path
            if((p=index(l, ' ')) || (p=index(l, '\t')) || (p=index(l, '\n')) || strlen(l)) {

                addr=l;
                if(p) *p='\0';
                // resolve the host
                if(!*host) host="127.0.0.1";

                {

                    struct hostent *he;

                    if(!(he=gethostbyname(host)) 
                        && (end->addr.in.sin_addr.s_addr=inet_addr(host)) == 0xffffffff) {
                        
                         // check if this is a generic chassis number specification
                         // 
                         int num;
                         if((num=is_cnum(host)) >=0) {
                         
                              end->num=num;
                         }
                         else {
                            dbg(0,0,0, "Unknown host '%s' @ line %d\n", host, curline);
                            return 0;
                        }
                    }
                    if(he) end->addr.in.sin_addr=*( struct in_addr*)he->h_addr;

                }
                
                // resolve l4 addr
                if(!strcmp(type, "tcp")) end->type=END_TYPE_TCP;
                else if(!strcmp(type, "udp")) end->type=END_TYPE_UDP;
                else if(!strcmp(type, "afunix")) end->type=END_TYPE_UNIX;
                else if(!strcmp(type, "dev")) end->type=END_TYPE_DEVICE;
                else {

                    dbg(0,0,0,"Invalid type for addr '%s' @ line %d (one of : tcp, udp, afunix)\n", addr, curline);
                    return 0;
                }

                // resolve addr
                if(end->type==END_TYPE_TCP || end->type==END_TYPE_UDP) {
                
                    end->addr.in.sin_family=AF_INET;
                    end->addr.in.sin_port=htons(atoi(addr));
                    if(!end->addr.in.sin_port) {
                    
                        // try to use service interface
                        struct servent *s=getservbyname((char*)addr, type);
                        
                        if(!s) {
                        
                            int val;
                        
                            // could be an expression
                            if(!(val=eval((uint8_t*)addr, 
                                    (uint8_t**)(&addr), 0))) {
                        
                                dbg(0,0,0, "Invalid service '%s' specified @ line %d\n", addr, curline);
                                return 0;
                            }
                            else end->addr.in.sin_port=htons(val);
                        
                        }
                        else end->addr.in.sin_port=s->s_port;
                    
                    }
                    
                } else if(end->type==END_TYPE_UNIX) {
                
                    end->addr.un.sun_family=AF_UNIX;
                    strncpy(end->addr.un.sun_path, addr, sizeof end->addr.un.sun_path);

                } else if(end->type==END_TYPE_DEVICE) {
                
                    end->addr.devname=strdup(addr);

                }
                free(li);
                return 1;
            }
        }
    }
    dbg(0,0,0,"Not enough ':' @ line '%d'\n", curline);
    return 0;    
}

// scan all interfaces looking for a match for address 'addr'
static int is_mine(int addr)
{
	char buf [2048];
	struct ifconf ic;
    int i, sock, thisAddr;
    struct ifreq *ifp;
    
    // we always own this one on the target
    if(addr == INADDR_ANY) return 1;

	if ((sock = socket (AF_INET, SOCK_DGRAM, IPPROTO_UDP)) < 0)
		dbg(0,1,1, "socket creation failed");
    ic.ifc_len = sizeof buf;
    ic.ifc_ifcu.ifcu_buf = (caddr_t)buf;
    if(ioctl(sock, SIOCGIFCONF, &ic) < 0) dbg(0,1,1,"SIOCGIFCONF");
    close(sock);
    for (i = 0; i < ic.ifc_len; i += sizeof (struct ifreq)) {
         ifp = (struct ifreq *)((caddr_t)ic.ifc_req + i);
         thisAddr=((struct sockaddr_in*)(&ifp->ifr_addr))->sin_addr.s_addr;
         if(addr==thisAddr)
             return 1;            
    }
    return 0;
}
    
static int processConfBuf(char *pbuf, int nbytes)
{
int pos;
fr_t *newList=0, *last=0;

    for(pos=0;pos<nbytes;pos++) if(pbuf[pos]=='^') pbuf[pos]='\n';
    if(dbglvl) fprintf(stderr, "%s", pbuf);
    for(pos=0;pos<nbytes;pos++) if(pbuf[pos]=='\n') pbuf[pos]='\0';
    curline=0;
    for(pos=0; pos<nbytes; pos +=strlen(pbuf+pos)+1) {

        char *tok, *line=strdup(pbuf+pos);

        fr_t *f=newFr();
        curline++;

        if(!(tok=strtok(line, " \t"))) continue;
        if(tok[0]=='#') continue;
        if(!parseOne(tok, &f->in)) goto err;
        if(!(tok=strtok(0, " \t"))) {

            dbg(0,0,0, "Missing destination field @ line %d\n ", curline);
            goto err;
        }
        if(!parseOne(tok, &f->out)) goto err;
        f->flags=0;
        if((tok=strtok(0, " \t"))) {

            if(!(parseFlags(tok, f))) goto err;
        }
        //
        // all set for this entry. Add to current list.
        // we only add it to our list if it's not found asis in the current list
        if(!findFr(f)) {
            f->next=newList;
            newList=f;
            if(!last) last=f;
        }
        //  check if this is ours.
        f->mine=is_mine(f->in.addr.in.sin_addr.s_addr);
        if(dbglvl) prpfr(f);
    }
    //
    // time to merge new and old
    //    
    // any FR that is not found anymore in the new list must be closed.
    // we also shorten the active list as we go
    
    {
    fr_t *fr=frlist, *prev=0;
    
        while(fr) {
        
            fr_t *next=fr->next;
        
            if(!(fr->flags & FR_FLAG_FOUND)) {
            
                closeFr(fr);
                if(prev) prev->next=next;
                else {

                    frlist=next;
                }
            }
            else prev=fr;
            fr=next;
        }
    }
    // link the 2 lists
    if(newList) {
        last->next=frlist;
        frlist=newList;
    }
    return 1;
err:
    {
    fr_t *f=newList;
    
        while(f) {
        
            fr_t *next=f->next;
            free(f);
            f=next;
        }
    }
    return 0;
}        
        
static int readConf()
{
    FILE *p;
    char *fmt="cpp -P %s";
    char cmd[1000];
    int totr=0, n;
    #define BUFSIZE 100000
    char *buf=calloc(1, BUFSIZE);

    sprintf(cmd, fmt, confFile(PFRS_FNAME));
    dbg(1, 0, 0, "CPP cmd '%s'\n", cmd);

    p=popen(cmd, "r");
    //
    // Read in the entire output form the pipe
    while(totr < BUFSIZE && (n=fread(buf+totr, 1, BUFSIZE-totr, p)) > 0) {
        totr+=n;
    }
    pclose(p);
    
    if(!processConfBuf(buf, totr)) goto err;
    free(buf);
    return 1;
    
err:

    free(buf);
    return 0;
}

static void hup_handler(int sig)
{
    dbg(0,0,0,"Got HUP: re-reading config.\n");
    redoConf=1;
    signal(SIGHUP, hup_handler);
}

static void usr1_handler(int sig)
{
    dbglvl++;
    dbg(0,0,0,"Debug level now %d\n", dbglvl);
    signal(SIGUSR1, usr1_handler);
}

static void usr2_handler(int sig)
{
    if(dbglvl) dbglvl--;
    dbg(0,0,0,"Debug level now %d\n", dbglvl);
    signal(SIGUSR2, usr2_handler);
}

static void usage()
{
    dbg(0,0,1,
"usage: pfd [-P<port>] [-f<configDirectory>] [-i<client interface>] [-C<server>] [-d[-d ]...]\n"
"       -P Specifies the info port number (default:12012)\n"
"       -f Specifies the configuration directory (required)\n"
"       -d will increment debug level and keep pfd in foreground (defaut:no debug)\n"
"       -i specifies the interface name from which clients will broadcast (default:"CLIENT_INT")\n"
"       -C This option should be used when instantiating pfd on the client host (default: off)\n"
    );
    exit(1);
}

//
// Setup the information port that pfdinfo(1) will be using
static int infoFd=-1;
typedef struct infoCon_s {

    int inuse;
    int fd;
    
} infoCon_t;
#define MAX_ICONS 100
static infoCon_t icons[MAX_ICONS];
#define MAX_CCONS 100
static infoCon_t ccons[MAX_CCONS];
static void sendMsg(int fd, char *fmt, ...)
{
va_list ap;
char buf[200];
    va_start(ap, fmt);
    vsnprintf(buf, sizeof buf, fmt, ap);
    write(fd, buf, strlen(buf));
}


static void sendCoords(int fd, int cnum, int snum, int nnum, char *name)
{
fr_t *f;

    for(f=frlist; f; f=f->next) {
        if((!cnum || f->cnum == cnum) && f->snum == snum && f->nnum == nnum
            && !strcmp(f->name, name)) {
            
                sendMsg(fd, "ok %s %d %-15s %d:%d:%d\n", 
                    inet_ntoa(f->in.addr.in.sin_addr), 
                    ntohs(f->in.addr.in.sin_port), 
                    name,
                    f->cnum,
                    snum,
                    nnum
                );
                return;
        }
    }
    sendMsg(fd, "c/s/n %d/%d/%d:%s not found.\n", cnum, snum, nnum, name);
}
static short getCtlPort()
{
    return ctlPort;
}

static int infoSetup()
{
int sock, on=1;
struct sockaddr_in addr;

    if((sock=socket(AF_INET, SOCK_STREAM, 0)) >= 0) {
        setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &on, sizeof on);
        addr.sin_family=AF_INET;
        addr.sin_addr.s_addr=INADDR_ANY;
        addr.sin_port=htons(getCtlPort());
        if(bind(sock, (struct sockaddr *) &addr, sizeof addr) >= 0) {
            if(listen(sock,64)) dbg(0,1,0, "info listen");
            infoFd=sock;
            return 1;
        } else dbg(0,1,0, "info bind");
        close(sock);
    } else dbg(0,1,0, "info socket");
    return 0;
}
static int infoSetFds(fd_set *fdset, int maxfd)
{
int idx;
    if(infoFd >= 0) setfd(infoFd);
    for(idx=0; idx<MAX_ICONS; idx++) {

        if(icons[idx].inuse) setfd(icons[idx].fd);

    }
    return maxfd;
}
static void infoProcessFds(fd_set *fdset)
{
    if(FD_ISSET(infoFd, fdset)) {
    
        // accept a new client connection
        
        struct sockaddr_in cliAddr;
        int sock;
        socklen_t cliLen;
        cliLen = sizeof(cliAddr);

        // new incoming connection
        if((sock=accept(infoFd,(struct sockaddr *) &cliAddr, &cliLen)) < 0) 
            dbg(0,1,0,"Accept on infofd failed");
        else {

            // add this to our connection list
            int idx;
            // find a free slot
            dbg(1,0,0,"Accepted CTL connection on fd %d\n", sock);
            for(idx=0; idx<MAX_ICONS; idx++) {

                if(!icons[idx].inuse) break;

            }
            if(idx==MAX_ICONS) {
                dbg(0,0,0, "Maximum number of active info sessions reached[%d]\n", MAX_ICONS);
                close(sock);
            }
            else {

                icons[idx].fd=sock;
                icons[idx].inuse=1;

            }
        }
    }
    // check info sessions
    {
        int idx;
        for(idx=0; idx<MAX_ICONS; idx++) {

            if(icons[idx].inuse && FD_ISSET(icons[idx].fd, fdset)) {
            
                // process that command
                char cmd[200];
                int n;
                
                // read in the command
                if((n=read(icons[idx].fd, cmd, sizeof cmd))>0) {
                
                    cmd[n]='\0';
                    dbg(1,0,0,"[%d] cmd '%s'\n", icons[idx].fd, cmd);
        
                    switch(cmd[0]) {
                    
                        case 'q' :{ // quit
                        
                            goto closeit;
                        
                        }
                        break;
                    
                        case 'a' :{
                        
                            // wants coordinates associated with chassis, node type, instance tripplet
                            // read in the tripplet
                            int cnum, n;
                            char name[40]={'\0'};
                            if((n=sscanf(cmd+1, "%d %40s", &cnum, name)) < 1) {
                                sendMsg(icons[idx].fd, "Usage is 'a <chassis #> [<service name>]\n");
                            }
                            else {
                            
                                fr_t *f;
                                for(f=frlist;f;f=f->next) {
                                    if((!cnum || f->cnum==cnum) && (n==1 || !strcmp(f->name, name))) {
                                        sendCoords(icons[idx].fd,cnum, f->snum, f->nnum, f->name);
                                    }
                                }
                            }
                        }
                        break;
                        case 'l' :{
                        
                            // wants coordinates associated with chassis, node type, instance tripplet
                            // read in the tripplet
                            int cnum, inum;
                            char type[40], name[40];
                            if(sscanf(cmd+1, "%d %40s %d %40s", &cnum, type, &inum, name) != 4) {
                                sendMsg(icons[idx].fd, "Usage is 'l <chassis #> <node type> "
                                        "<instance #> <service name>\n");
                            }
                            else {
#if 0                            
                                // look it up
                                // the FR entries keep track of c/s/n .
                                // we need to map the type/instance to s and n
                                int i;
                                for(i=0;i<nnodes; i++) {
                                
                                    if(!strcmp(nodes[i].type, type) && nodes[i].inum==inum) break;
                                
                                }
                                if(i==nnodes) sendMsg(icons[idx].fd, 
                                    "Type '%s' instance %d not found.\n", type,inum);
                                else {
                                    sendCoords(icons[idx].fd,cnum, nodes[i].snum, nodes[i].nnum, name);
                                }
#endif
                                sendMsg(icons[idx].fd, "Type '%s' instance %d not found.\n", type,inum);
                            }
                        }
                        break;
                        case 'p' :{
                        
                            // wants coordinates associated with chassis, node type, instance tripplet
                            // read in the tripplet
                            int cnum, snum, nnum;
                            char name[40];
                            if(sscanf(cmd+1, "%d %d %d %40s", &cnum, &snum, &nnum, name) != 4) {
                                sendMsg(icons[idx].fd, "Usage is 'c <chassis #> <slot #> <node #> <service name>\n");
                            }
                            else {
                            
                                sendCoords(icons[idx].fd,cnum, snum, nnum, name);
                            }
                        }
                        break;
                        case '?': {
                            // need help output here...
                        }
                        break;
                        case '\n': case '\r': break;
                        default:
                            dbg(0,0,0,"Invalid command '%c' received.\n", cmd[0]);
                            sendMsg(icons[idx].fd, "Invalid command '%c'\n", cmd[0]);
                        break;
                    
                    } 
                }
                else if(n==0) {
closeit:                
                    dbg(1,0,0,"Connection closed fd %d\n", icons[idx].fd);
                    icons[idx].inuse=0;
                    close(icons[idx].fd);
                
                }
                else if(errno != EINTR) {
                
                    dbg(0,1,0,"Error on read fd %d, closing", icons[idx].fd);
                    icons[idx].inuse=0;
                    close(icons[idx].fd);
                
                }
            }
        }
    }
}

int serverFd=-1;
static int serverSetup()
{
int sock, on=1;
struct sockaddr_in addr;
struct ifreq ifr;

    if((sock = socket(PF_INET, SOCK_DGRAM, 0)) <+ 0) 
        dbg(0,1,1,"socket error [clientSetup]");

    strncpy(ifr.ifr_name, clientInt, IFNAMSIZ);
    if (ioctl(sock, SIOCGIFBRDADDR, &ifr))
        dbg(0,1,1,"Interface query failed for '%s'", clientInt);

    close(sock);
    if((sock=socket(AF_INET, SOCK_STREAM, 0)) >= 0) {
        setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &on, sizeof on);
        addr.sin_family=AF_INET;
        addr.sin_addr.s_addr=INADDR_ANY;
        addr.sin_port=htons(getCtlPort()+1);
        if(bind(sock,(struct sockaddr *) &addr, sizeof addr ) >= 0) {
            if(listen(sock,64)) dbg(0,1,0, "info listen");
            serverFd=sock;
            return 1;
        } else dbg(0,1,0, "info bind");
        close(sock);
    } else dbg(0,1,0, "info socket");
    return 0;
}
static int serverSetFds(fd_set *fdset, int maxfd)
{
int idx;
    if(serverFd >= 0) {
        setfd(serverFd);
    }
    for(idx=0; idx<MAX_CCONS; idx++) {

        if(ccons[idx].inuse) setfd(ccons[idx].fd);

    }
    return maxfd;
}
static void serverSendConfig(int this)
{
    // prfs specification expects the ONTARGET to be defined so
    // that corresponding target port map can be generated.
    char *fmt="cpp -o - -DONTARGET -P %s";
    char cmd[1000];
    int n, totr=0, idx;
    #define BUFSIZE 100000
    char *buf=calloc(1, BUFSIZE);

    snprintf(cmd, sizeof cmd, fmt, confFile(PFRS_FNAME));
    FILE *p=popen(cmd, "r");
    //
    // Read in the entire output form the pipe
    while(totr < BUFSIZE && (n=fread(buf+totr, 1, BUFSIZE-totr, p)) > 0) {
        totr+=n;
    }
    pclose(p);
    //
    // Send to that client or all of them
    //
    for(idx=0; idx<MAX_CCONS; idx++) {
    
        // when called with this == -1 =? send to every client
        // This is used by the processConf
        if((this==-1 && ccons[idx].inuse) || this==idx) {
        
            int totw=0, this=totr, nw;
            
            while(this && (nw=write(ccons[idx].fd, buf+totw, this)) > 0) {
                totw+=nw;
                this-=nw;
            }
            if(nw<0) {

                // some error sending this stuff accross
                dbg(0,1,0, "Could not send config to client on fd %d[idx=%d]\n", ccons[idx].fd,idx);
                close(ccons[idx].fd);
                ccons[idx].inuse=0;
                break;
            }
            if(ccons[idx].inuse) {
                dbg(1,0,0,"Send configuration to client on fd %d[ idx=%d].\n", ccons[idx].fd,idx);
                write(ccons[idx].fd, "[DONE]", 6);
            }
        }
    }
    free(buf);
}

static int processConf()
{
    resetFoundFlags();
    if(readConf()) {
        // let all clients know
        serverSendConfig(-1);
        return 1;
    }
    return 0;
}

static void serverProcessFds(fd_set *fdset)
{
int idx;

    if(FD_ISSET(serverFd, fdset)) {
    
        // accept a new client connection
        
        struct sockaddr_in cliAddr;
        int sock;
        socklen_t cliLen;
        cliLen = sizeof(cliAddr);

        // new incoming connection
        if((sock=accept(serverFd,(struct sockaddr *) &cliAddr, &cliLen)) < 0) 
            dbg(0,1,0,"Accept on serverFd failed");
        else {

            // add this to our connection list
            int idx;
            // find a free slot
            dbg(1,0,0,"Accepted CLIENT connection on fd %d\n", sock);
            for(idx=0; idx<MAX_CCONS; idx++) {

                if(!ccons[idx].inuse) break;

            }
            if(idx==MAX_CCONS) {
                dbg(0,0,0, "Maximum number of active info sessions reached[%d]\n", MAX_CCONS);
                close(sock);
            }
            else {
                ccons[idx].fd=sock;
                ccons[idx].inuse=1;
                serverSendConfig(idx);
            }
	    }
    }
    // check out the client connections themselves.
    for(idx=0; idx<MAX_CCONS; idx++) {

        if(ccons[idx].inuse && FD_ISSET(ccons[idx].fd, fdset)) {
        
            char buf[100];
            int nr;
            
            // at this point the client should not be talking to us.
            // that must be a diconnection
            while((nr=read(ccons[idx].fd, buf, sizeof buf)) > 0);
            if(nr) {
            
                dbg(0,0,0, "Got %d bytes from client.\n", nr);
            
            }
            else {
                
                dbg(0, 0, 0, "Lost connection from client on fd %d[%d].\n", ccons[idx].fd, idx);
                close(ccons[idx].fd);
                ccons[idx].fd=-1;
                ccons[idx].inuse=0;
            }        
        }
    }
}
int clientFd=-1;

static void clientSetup()
{
int sock, on=1;
struct hostent *he;
struct sockaddr_in sockaddr;

    if(clientFd<0) {
        dbg(1,0,0,"Client : trying to connect to server...");
        if(!(he=gethostbyname(server))) {

            if((sockaddr.sin_addr.s_addr=inet_addr(server)) == 0xffffffff)
                dbg(0,0,1, "Unknown server '%s'\n", server);
        }
        else sockaddr.sin_addr=*( struct in_addr*)he->h_addr;

        if((sock=socket(AF_INET, SOCK_STREAM, 0)) >= 0) {
            setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &on, sizeof on);
            sockaddr.sin_family=AF_INET;
            sockaddr.sin_port=htons(getCtlPort()+1);
            if(connect(sock, (struct sockaddr *)&sockaddr, sizeof sockaddr) >= 0) {
                clientFd=sock;
                dbg(1,0,0,"Success[fd %d].\n", clientFd);
                return;
            }
            close(sock);
        }
        if(clientFd<0) dbg(1,0,0,"Failed\n");
    }
}

static void clientProcessFds(fd_set *fdset)
{
    if(clientFd>=0) {
    
        if(FD_ISSET(clientFd, fdset)) {
            #define CONF_SIZE 10240
            char *buf=calloc(1, CONF_SIZE);
            int pos=0, nr, this=CONF_SIZE;
            // read connection for our config.
            while(this && (nr=read(clientFd, buf+pos, this)) > 0) {
                pos+=nr;
                this-=nr;
                if(pos>6 && !strcmp(buf+pos-6, "[DONE]")) break;
            }
            if(nr<=0) {
                dbg(0,0,0,"Could not get config from server.\n");
                close(clientFd);
                clientFd=-1;
            } else {
                buf[pos]='\0';
                dbg(1,0,0, "Read client configuration:\n----\n");
                dbg(1,0,0, "%s\n----\nProcessing.\n", buf);
                buf[pos-6]='\0';
                processConfBuf(buf, pos-6);
            }
        }
    }    
}

static int clientSetFds(fd_set *fdset, int maxfd)
{
     if(clientFd >= 0) setfd(clientFd);
     return maxfd;
}

int main(int argc, char **argv)
{
time_t lastpoll=0;
int c;
extern char *optarg;
sigset_t sigset, psigs;

    sigemptyset(&sigset);
    sigaddset(&sigset, SIGHUP);

    sigprocmask(SIG_BLOCK, &sigset, 0);
    // sigblock(sigmask(SIGHUP));
    signal(SIGUSR1, usr1_handler);
    signal(SIGUSR2, usr2_handler);
    signal(SIGHUP,   hup_handler);
    openlog("PFD",  LOG_NDELAY, LOG_DAEMON);
    
    // parse command line arguments
    while ((c = getopt(argc, argv, "i:D:df:C:")) != EOF) {
        switch (c) {
            case 'D':
                ctlPort=atoi(optarg);
            break;
            case 'd':
                usr1_handler(0);
            break;
            case 'f':
                confDir=optarg;
            break;
            case 'C':
                isClient=1;
                server=optarg;
            break;
            case 'i':
                clientInt=optarg;
            break;
            default :  case '?':
                usage();
        }
    }
    
    // client needs to get config from server
    // Server will run the config again with -DON_TARGET and deliver the result
    // over the connection.
    if(isClient) {
    
        // use the specified interface to broadcast to the server
        clientSetup();
    
    }
    else {
    
        if(!confDir) {
            dbg(0,0,0, "Use -f option to specific configuration directory\n");
            usage();
        }
        if(!processConf()) 
            dbg(0,0,1, "Error reading configuration files.\n");
    
        // setup info port
        if(!infoSetup()) exit(1);

        // setup client service 
        if(!serverSetup()) exit(1);
    }
    
    // deamonize ?
    if(!dbglvl) {
        int pid;
    
        if((pid=fork()) > 0) exit(0);
        else if(pid<0) dbg(0, 1, 1, "Fork failed");
    }
    while(1) {
    
        struct timeval tv={ tv_sec: POLL_INTERVAL };
        fd_set fdset;
        int maxfd=0, n;
        
        // check on the HUP signal
        while(1) {
            sigpending(&psigs);
            if(sigismember(&psigs, SIGHUP)) {
                sigprocmask(SIG_UNBLOCK, &sigset, 0);
                sigprocmask(SIG_BLOCK, &sigset, 0);
            }
            else break;
        }
        FD_ZERO(&fdset);
        if(!isClient) {
            maxfd=infoSetFds(&fdset, maxfd);
            maxfd=serverSetFds(&fdset, maxfd);
        }
        else {
            maxfd=clientSetFds(&fdset, maxfd);
        }
        maxfd=frSetFds(&fdset, maxfd);
        
        sigprocmask(SIG_UNBLOCK, &sigset, 0);
        if((n=select(maxfd+1, &fdset, 0, 0, &tv))>0) {
            frProcessFds(&fdset);
            if(!isClient) {
                infoProcessFds(&fdset);
                serverProcessFds(&fdset);
            } else clientProcessFds(&fdset);
        }
        if(n<0) {
        
            if(errno != EINTR) {
        
                dbg(0,1,1,"Select failed");
            }
            else {
                dbg(1,0,0,"Select was interupted.\n");
                if(redoConf) {
                
                    processConf();
                    redoConf=0;
                }
            }
        
        }
        if((time(0) - lastpoll) > POLL_INTERVAL) {
            frPollSocks();
            if(isClient) clientSetup();
            lastpoll=time(0);
        }
    }
}
