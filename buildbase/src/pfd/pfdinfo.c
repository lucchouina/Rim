#include <stdlib.h>
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
#include <ctype.h>
#include <fcntl.h>
/*
    Simple program to query the local PFD domains
*/
static int dbglvl=0;

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
    fprintf(stderr, "%s", msg);
    va_end(ap);
    if(die) exit(1);
}

static int listDomains(char *domain)
{
int port=0;
FILE *f=fopen(DOMAIN_FILE, "r");
    if(!f) dbg(0,1,1,"Could not open %s on this host. PFD not installed.", DOMAIN_FILE);
    {
    char name[100];
    int p;

        while(fscanf(f, "%s %d\n", name, &p)==2) {

            if(domain) {
                if(!strcmp(name, domain)) {

                    port=p;
                    break;
                }
            }
            else dbg(0,0,0,"%s\n", name);

        }
        if(domain && !port) {
            dbg(0,0,1,"Domain '%s' not found in '%s'\n", domain, DOMAIN_FILE);
        }
    }
    return port;
}  
static void usage()
{
    dbg(0,0,0,"Usage pfdinfo <domainchasssis#> <nodeInstance> <service>\n"
              "      pfdinfo <domainchasssis#> <service>\n"
              "      pfdinfo <domainchasssis#>\n"
              "      pfdinfo <domain>\n"
              "Examples:\n"
              "     pfdinfo atca1 scComE0 telnet\n"
              "         Print entry for telnet service for scComE0\n"
              "     pfdinfo atca1 telnet\n"
              "         List telnet service entries for all nodes of atca1\n"
              "     pfdinfo atca1\n"
              "         List all nodes and services for this chassis\n"
              "     pfdinfo atca\n"
              "         List all chassies defined in domain atca\n"
              );
    dbg(0,0,0,"List of available domains :\n");
    (void)listDomains(0);
    exit(1);
}

#define WIN_YPIXES  200
#define WIN_XPIXES  700
static int ypos=0, xpos=0, yinc, xinc, ymax, xmax; 
static void initPos(int nwins, int *pny, int *pnx)
{
FILE *p=popen("xdpyinfo  | grep -i dimension | awk '{print $2}' | awk -Fx '{printf(\"%s %s\", $1, $2);}'", "r");
int maxwins, ny=WIN_YPIXES, nx=WIN_XPIXES, w, h;
char buf[100];
int n;


    if((n=read(fileno(p), buf, sizeof buf))<0)
        dbg(0,1,1,"Read error on pipe");

    buf[n]=0;
    if(sscanf(buf, "%d %d", &w, &h) != 2) {
    
        dbg(0,0,1,"Could not query display size.\n");
    
    }
    xmax=w;
    ymax=h;
    maxwins=(h/ny) * 2;
    if(nwins>maxwins) {
    
        ny=(h*2)/maxwins;
    
    }
    yinc=ny;
    if(nx*2 > w) nx=w/2;
    xinc=nx;
    // half the display width
    *pnx=nx;
    *pny=ny;
}

static void getPos(int *x, int *y)
{
    *y=ypos;
    *x=xpos;
    ypos+=yinc;
    if(ypos+yinc > ymax) {
        ypos=0;
        xpos+=xinc;
        if(xpos+xinc > xmax) {
            xpos=0;
        }
    }
}
#define INFONAME "pfdinfo"
#define INFOSIZE (sizeof INFONAME -1)
int main(int argc, char ** argv)
{
char *domain=0, *chassis=0, *nodestr=0, *service=0;
char *termcmd=0, *cards=0, *termtype=0;
int port=0, sock, printit=0;

    if(!argv[1] || argv[1][0]=='-') usage();

    if(argc==4) {
        domain=argv[1];
        nodestr=argv[2];
        service=argv[3];
    }
    else if(argc==3) {
    
        domain=argv[1];
        service=argv[2];
    }
    else if(argc==2) {
    
        domain=argv[1];
    
    }
    else usage();
    
    if(strlen(argv[0]) >= INFOSIZE
        && !strcmp(argv[0]+strlen(argv[0])-INFOSIZE,INFONAME)) 
            printit=1;
        
    // look for the last non-numeric character in the chassis name
    {
    char *p=domain+strlen(domain)-1;
    
        while(p>domain) {
            if(isdigit(*p)) {
                p--;
                continue;
            }
            chassis=strdup(p+1);
            *(p+1)='\0';
            break;
        }
    }
    
    if((nodestr || service) && !chassis) usage();
    
    if(!(termcmd=getenv("TERMCMD"))) termcmd="gnome-terminal";
    cards=getenv("CARDS");
    if(service) termtype=service;
    else if(!(termtype=getenv("TERMTYPE"))) termtype="telnet";
    
    // open the domains file and find this domain
    port=listDomains(domain);
    
    // open a connection to the local pfd server for this domain
    {
    int on=1;
        if((sock=socket(AF_INET, SOCK_STREAM, 0)) >= 0) {
            struct sockaddr_in addr;
            addr.sin_addr.s_addr=INADDR_ANY;
            addr.sin_family=AF_INET;
            addr.sin_port=htons(port);
            
            setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &on, sizeof on);

            if(connect(sock, (struct sockaddr *) &addr, sizeof(addr)))
                dbg (0,1,1,"Could not connect to local PFD server on port %d\n", port);
        }
        else dbg(0,1,1,"Could not open socket");
    }
    
    // write the command
    {
    FILE *fsock=fdopen(sock, "w");
    
        if(!chassis[0]) chassis="0";
        if(service) fprintf(fsock, "a %s %s\n", chassis, service);
        else fprintf(fsock, "a %s\n", chassis);
        fflush(fsock);
        // read the reponce and print it
        {
            #define MAXBYTES (1024*1024)
            char *buf=(char*)calloc(1, MAXBYTES+1), *p;
            int n, total=0, retries=1, nwins=0, ny, nx, nxc, nyc;
            char status[10];
            char ip[40], pstr[20], svc[20], domain[20], inst[40];

            fcntl(sock, F_SETFL, O_NONBLOCK);

            while(total < MAXBYTES) {
            
                if((n=read(sock, buf+total, MAXBYTES-total))<0) {
                    if(errno==EAGAIN) {
                        if(retries--) {
                            usleep(100);
                            continue;
                        } else break;
                    }
                    dbg(0,1,1,"Read error");
                }
                total += n;
            }
            dbg(1,0,0, "Got answer '%s'\n", buf);
            // replace all '\n' by '\0'
            for(n=0;n<total;n++) if(buf[n]=='\n') buf[n]='\0';
            
            // count number of windows
            for(p=buf; *p; p+=strlen(p)+1) {

                if(sscanf(p, "%10s %40s %20s %20s %20s %40s\n",
                    status, ip, pstr, svc, domain, inst)==6){ 

                    if(strcmp(status, "ok")) dbg(0,0,1,"Error returned by server\n");
                    if(nodestr && strcmp(inst, nodestr)) continue;
                    // check card match
                    if(cards && !strstr(cards, inst)) continue;
                    // check service match
                    if(strcmp(termtype, svc)) continue;
                    nwins++;
                }
            }
            if(!nwins) {
            
                dbg(0,0,1,"No match found for node (%s) cards (%s) type (%s)\n",
                    nodestr?nodestr:"all",
                    cards?cards:"all",
                    termtype); 
            }
            
            
            // init position and size
            if(!printit) {
                initPos(nwins, &ny, &nx);
                nxc=(nx-10)/8;
                nyc=(ny-10)/16;
            }

            for(p=buf; *p; p+=strlen(p)+1) {

                if(sscanf(p, "%10s %40s %20s %20s %20s %40s\n",
                    status, ip, pstr, svc, domain, inst)==6){ 

                    if(strcmp(status, "ok")) dbg(0,0,1,"Error returned by server\n");
                    if(nodestr && strcmp(inst, nodestr)) continue;
                    if(printit) {
                        dbg(0,0,0,"%s %s %-12s %-10s %10s\n", ip, pstr, svc, domain, inst);
                    } else {
                        dbg(1,0,0,"%s %s %-12s %-10s %10s\n", ip, pstr, svc, domain, inst);
                        int ypos, xpos;
                        // check card match
                        if(cards && !strstr(cards, inst)) continue;
                        // check service match
                        if(strcmp(termtype, svc)) continue;
                        //
                        // ok. Start term.
                        getPos(&xpos, &ypos);
                        if(!fork()){
                            char cmd[200];
                            snprintf(cmd,sizeof cmd, 
                                "%s --geometry %dx%d+%d+%d --title %s:%s:%s -e 'telnet %s %s' 1>/dev/null 2>&1", 
                                termcmd,
                                nxc,nyc,xpos,ypos,
                                domain, inst, svc,
                                ip, pstr);
                            system(cmd);
                            exit(0);
                        }
                    }
                }
            }
        }
    }
    exit(0);
}
