#include <fcntl.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdlib.h>
#include <getopt.h>
#include <stdarg.h>

#define TYPE_UBL    0
#define TYPE_SPL    1

#define DEFAULT_TYPE        "spl"
#define ENTRY_DEFAULT       0xc1080000
#define LOAD_DEFAULT        ENTRY_DEFAULT
#define UBL_ENTRY_DEFAULT   0x80000000
#define UBL_LOAD_DEFAULT    UBL_ENTRY_DEFAULT
#define FNAME_DEFAULT       "./u-boot.bin"
#define PNAME_DEFAULT       "./spl/u-boot-spl.bin"
#define MAGIC               0xa1aced66

static int dbglvl=1;
static int entry=ENTRY_DEFAULT;
static int loadaddr=LOAD_DEFAULT;
static int pentry=UBL_ENTRY_DEFAULT;
static int ploadaddr=UBL_LOAD_DEFAULT;
static const char *type=DEFAULT_TYPE;
static const char *fname=FNAME_DEFAULT;
static const char *pname=PNAME_DEFAULT;

/*
    UBL preamble
*/
static int ubl[] = {

    0x41504954,
    0x5853590d, 0x00030006, 0x00180001, 0x00000205, 0x0000000e,
    0x5853590d, 0x00080003, 0x18010001, 0x00000002, 0x000000c4, 0x00134622, 0x20923209, 0x8414c722, 0x00000249, 0x00000000,
    0x5853590d, 0x00010007, 0x00050003 ,
    0x5853590d, 0x00010007, 0x000e0003 ,
    0x5853590d, 0x00010007, 0x01030003 ,
    0x5853590d, 0x00010007, 0x010c0003,
    0x5853590d, 0x00030008, 0x00000000, 0xffffffff, 0x88488888 ,
    0x5853590d, 0x00030008, 0x00000001, 0xffffffff, 0x88888888 ,
    0x5853590d, 0x00030008, 0x00000002, 0xffffffff, 0x88888888 ,
    0x5853590d, 0x00030008, 0x00000003, 0xffffffff, 0x88888888,
    0x5853590d, 0x00030008, 0x00000004, 0xffffffff, 0x22222288 ,
    0x5853590d, 0x00030008, 0x00000005, 0xffffffff, 0x88111111 ,
    0x5853590d, 0x00030008, 0x00000006, 0xffffffff, 0x88888888 ,
    0x5853590d, 0x00030008, 0x00000007, 0xffffffff, 0x88888888,
    0x5853590d, 0x00030008, 0x00000008, 0xffffffff, 0x88888888 ,
    0x5853590d, 0x00030008, 0x00000009, 0xffffffff, 0x88888888 ,
    0x5853590d, 0x00030008, 0x0000000a, 0xffffffff, 0x88222222 ,
    0x5853590d, 0x00030008, 0x0000000b, 0xffffffff, 0x88888888,
    0x5853590d, 0x00030008, 0x0000000c, 0xffffffff, 0x88888888 ,
    0x5853590d, 0x00030008, 0x0000000d, 0xffffffff, 0x88888811 ,
    0x5853590d, 0x00030008, 0x0000000e, 0x000000ff, 0x00000088 ,
    0x5853590d, 0x00030008, 0x0000000f, 0x00000000, 0x00000000,
    0x5853590d, 0x00030008, 0x00000010, 0xfffffff0, 0x88888880 ,
    0x5853590d, 0x00030008, 0x00000011, 0x000000ff, 0x00000088 ,
    0x5853590d, 0x00030008, 0x00000012, 0xffffff00, 0x88888800 ,
    0x5853590d, 0x00030008, 0x00000013, 0xffffffff, 0x18888888,
    0x58535901, /* <load address> <size> */
};

/*
0002000 a1aced66 c1080000 0000014f 00000075
0002020 c1080000 00000000 00000000 00000000
0002040 00000000 00000000 00000000 00000000
*/
char *prog;

static void
usage()
{
    printf("usage: %s [ -t type ]  [ -u uboot.bin ] [ -[lL] load address ] [ -[eE] entry point ] [-p primer] device\n", prog);
    printf("where: device is the device name of file name to write too\n");
    printf("       t : type of sd format. Either 'ubl' or 'spl' [default: %s] \n", DEFAULT_TYPE);
    printf("       u : uboot file name [default: ./u-boot.bin] \n");
    printf("         e : u-boot entry point address [default: load address ] \n", ENTRY_DEFAULT);
    printf("         l : u-boot load address [default: 0x%08x] \n", LOAD_DEFAULT);
    printf("       p : primer file (either spl or ubl) [default: ubl ] \n");
    printf("         E : ubl/spl entry point address [default: load address ] \n", UBL_ENTRY_DEFAULT);
    printf("         L : ubl/spl load address [default: 0x%08x] \n", UBL_LOAD_DEFAULT);
    exit(1);
}

int die(int level, int doerr, char *fmt, ...)
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
    //free(myfmt);
    if(die) 
        exit(1);
}

static int 
is_ubl()
{
    if(!strcmp(type, "ubl")) return 1;
    return 0;
}

int
main(int argc, char **argv)
{
int fdDev, fdUboot, fdPrimer, fsize, psize, curpos, curblock;
int c;
extern char *optarg;
int bstart=0x75, blength, mstart=bstart-1, boffset=0;
int bdata[5];

    prog=argv[0];
    if(argc < 2) usage();
    
    // parse command line arguments
    while ((c = getopt(argc, argv, "e:l:t:u:E:L:p:")) != EOF) {
        switch (c) {
            case 'e':
                entry=atoi(optarg);
                if(entry < 0) { printf("Invalid u-boot entry point %s!\n", optarg); usage();} 
            break;
            case 'l':
                loadaddr=atoi(optarg);
                if( loadaddr< 0) { printf("Invalid load u-boot address %s!\n", optarg); usage();} 
            break;
            case 'E':
                pentry=atoi(optarg);
                if(pentry < 0) { printf("Invalid ubl/spl entry point %s!\n", optarg); usage();} 
            break;
            case 'L':
                ploadaddr=atoi(optarg);
                if( ploadaddr< 0) { printf("Invalid ubl/spl load address %s!\n", optarg); usage();} 
            break;
            case 't':
                if(strcmp(optarg,"ubl") && strcmp(optarg,"spl")) { 
                    printf("Invalid type %s - must be 'ubl' or 'spl'!\n", optarg); usage();} 
                type=optarg;
            break;
            case 'u':
                fname=optarg;
            break;
            case 'p':
                pname=optarg;
            break;
            default :  case '?':
                usage();
        }
    }

    if (optind >= argc) usage();

    (fdDev=open(argv[optind], O_RDWR+O_CREAT)) < 0 && die(0,1, "Error opening device or file %s\n", argv[optind]);
    
    /* check if there is an MBR */
    {
        int magic;
        (read(fdDev, &magic, 4) == 4) || die(0,1,"Error reading device");
        if(magic != 0x41504954) boffset++;
    }
    
    printf("Clearing 1 meg of card space starting at block %d\n", boffset);
    
    {
        char *buf=calloc(1024*1024, 1);
        lseek(fdDev, boffset*512, 0);
        write(fdDev, buf, 1024*1024) == 1024*1024 || die(0,1,"Error clearing device");
        free(buf);
    }
        
    ((fdUboot=open(fname, O_RDONLY)) < 0) && die(0,1,"Error opening uboot file %s\n", fname);
    
    ((fdPrimer=open(pname, O_RDONLY)) < 0)  && die(0,1,"Error opening primer file %s\n", pname);
    
    {
        struct stat buf;
        fstat(fdUboot, &buf) && die(0,1,"Error stat'ing uboot file %s\n", fname);
        fsize=buf.st_size;
        fstat(fdPrimer, &buf) && die(0,1,"Error stat'ing primer file %s\n", pname);
        psize=buf.st_size;
    }
    
    printf("Priming device/file %s with:\n", argv[1]);
    printf("    Type         : %s\n", type);
    printf("    u-boot       : %s\n", fname);
    printf("        Load address : 0x%08x\n", loadaddr);
    printf("        Entry point  : 0x%08x\n", entry);
    printf("        Block offset : %d\n", bstart);
    printf("        Block length : %d\n", blength);
    printf("    primer       : %s\n", pname);
    printf("        Load address : 0x%08x\n", ploadaddr);
    printf("        Entry point  : 0x%08x\n", pentry);
    printf("        Size         : %d\n", psize);
    
    /*
        Go to work.
    */
    
    /* drop the ubl or sbl */
    lseek(fdDev, boffset*512, 0);
    {
        char *pbuf=malloc(psize);
        (read(fdPrimer, pbuf, psize) == psize) || die(0,1,"Error reading primer file");
        
        if(!is_ubl()) {
        
            /* we need to prepend the AIS header defie herein. */
            write(fdDev, ubl, sizeof ubl) == sizeof ubl || die(0,1,"Error Writing AIS header");
            
            /* add load address and size */
            write(fdDev, &ploadaddr, sizeof ploadaddr) == sizeof ploadaddr || die(0,1,"Error Writing load address");
            write(fdDev, &psize, sizeof psize) == sizeof psize || die(0,1,"Error Writing psize");
        }
        /* write it */
        write(fdDev, pbuf, psize) != psize && die(0,1,"Error Writing primer file");
    }
    
    curpos=lseek(fdDev, 0, 1);
    printf("Ploader end offset - 0x%08x\n", curpos);
    curblock=(curpos+511)/512;
    printf("Uboot offset       - 0x%08x\n", curblock*512);
    lseek(fdDev, curblock*512, 0);
    
    {
    
        int bdata[5];
        bdata[0]=MAGIC;
        bdata[1]=loadaddr;
        bdata[2]=(fsize+511)/512;
        bdata[3]=curblock+1;
        bdata[4]=entry;
        
        (write(fdDev, bdata, sizeof bdata) == sizeof bdata) || die(0,1,"Error Writing MAGIC array");
    
    }
    
    curblock++;
    lseek(fdDev, curblock*512, 0);
    
    {
        char *buf=malloc(fsize);
        (read(fdUboot, buf, fsize) != fsize) && die(0,1,"Error reading uboot file %s : %s\n", argv[0], strerror(errno));
        (write(fdDev, buf, fsize) != fsize) && die(0,1,"Error writing uboot file %s : %s\n", argv[0], strerror(errno));
    }
    sync();
    exit(0);
}
