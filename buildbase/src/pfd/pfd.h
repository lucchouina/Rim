#ifndef __pfd_h__
#define __pfd_h__

#define DOMAIN_FILE "/etc/pfd.d/domains"

// end point object
typedef struct end_s end_t;
struct end_s {

    int type;
    union {
        struct sockaddr_un  un;
        struct sockaddr_in  in;
        char                *devname;
    } addr;
    int fd;     // listen socket for INET or file descriptor for UNIX or DEV
};


// one connection 
typedef struct con_s con_t;
struct con_s {

    time_t  created;        // time created
    time_t  last;           // time of last inbound activity
    int     infd;           // incoming socket
    int     outfd;          // outgoing socket
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

//
// define a transport object.
// Each object type will define methods for listening, accepting, reading, writing.
//
typedef trans_s {

    char *name;
    struct conObj_s *(*parse)(char *confStr);
    bool (*listen)(conObj_t *);
    void (*setFds)(fd_set *fdset);
    void (*processFds)(fd_set *fdset);
    void (*close)(conObj_t *); 
} trans_t;

//
// 
typedef struct conObj_s {

    trans_t *trans;     // associated transport
    void *tData;        // transport instance data  
    
} conObj_t;
    
#endif // __pfd_h__
