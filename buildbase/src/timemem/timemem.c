#include <stdlib.h>
#include <sys/types.h>
#include <limits.h>
#include <stdio.h>
#include <unistd.h>
#include <strings.h>
#include <string.h>
#include <fcntl.h>
#include <errno.h>
#include <stdarg.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

#define __USE_GNU
#include <dlfcn.h>
/**
   Simple overload library to force memory initliazation and return constant time() value.
   This way, mksqushfs command will produce the same file system, i.e. a filesystem
   with a constant md5 value if the source file tree is the same.
**/
typedef void * type_calloc(int number, size_t size);
typedef time_t type_time(time_t *t);
typedef int type_stat(int ver, const char *path, struct stat *buf);
typedef int type_fstat(int ver, int fd, struct stat *buf);

static  type_calloc *realCalloc;
static  type_time   *realTime;
static  type_stat   *realStat, *realLstat;
static  type_fstat  *realFstat;
//#define DEBUG 
#define TIME_2012_10_02 ((time_t)1349193600)

static void _init(void)
{
static int inited=0;

    if(!inited) {
        if(!(realCalloc    = (type_calloc*)    dlsym(RTLD_NEXT, "calloc")))
        {
            printf("Could not find realmalloc?!\n");
            exit(1);
        }

        if(!(realTime    = (type_time*)    dlsym(RTLD_NEXT, "time")))
        {
            printf("Could not find realtime?!\n");
            exit(1);
        }
        if(!(realLstat    = (type_stat*)    dlsym(RTLD_NEXT, "__lxstat64")))
        {
            printf("Could not find realLstat?!\n");
            exit(1);
        }
        if(!(realStat    = (type_stat*)    dlsym(RTLD_NEXT, "__xstat64")))
        {
            printf("Could not find realStat?!\n");
            exit(1);
        }
        if(!(realFstat    = (type_fstat*)    dlsym(RTLD_NEXT, "__fxstat64")))
        {
            printf("Could not find realFstat?!\n");
            exit(1);
        }
#ifdef DEBUG
        printf("Calloc is 0x%p, time is 0x%p\n", realCalloc, realTime);
        printf("State is 0x%p, lstat is 0x%p, fstat is 0x%p\n", realStat, realLstat, realFstat);
#endif
        inited=1;
    }
}

void *malloc(size_t numbytes)
{
    _init();
    return realCalloc(1, numbytes);
}

time_t time(time_t *t)
{
    _init();
    if(t) *t=0;
    return 0;
}

static void settimes(struct stat *buf)
{
        buf->st_atime=TIME_2012_10_02;
        buf->st_ctime=TIME_2012_10_02;
        buf->st_mtime=TIME_2012_10_02;
}


int __xstat64(int ver, const char *path, struct stat *buf)
{
    int ret;
    _init();
#ifdef DEBUG
    printf("xstat called on %s\n", path);
#endif
    ret=realStat(ver, path, buf);
    if(!ret) {
        settimes(buf);
    }   
    return ret;
}

int __lxstat64(int ver, const char *path, struct stat *buf)
{
    int ret;
    _init();
#ifdef DEBUG
    printf("lxstat called on %s\n", path);
#endif
    ret=realLstat(ver, path, buf);
    if(!ret) {
        settimes(buf);
    }   
    return ret;
}

int __fxstat64(int ver, int fd, struct stat *buf)
{
    int ret;
    _init();
#ifdef DEBUG
    printf("fxstat called on fd %d\n", fd);
#endif
    ret=realFstat(ver, fd, buf);
    if(!ret) {
        settimes(buf);
    }   
    return ret;
}
