#include <pcap/pcap.h>
#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>

int main(int argc, char **argv) {
    for (int i=1; i<argc; i++) {
        char err[PCAP_ERRBUF_SIZE];
        pcap_t *stream=pcap_open_offline(argv[i],err);
        if (!stream) {fprintf(stderr,"%s\n",err);return 1;}
        struct pcap_pkthdr *h;
        const u_char *bytes;
        int ret;
        int64_t first=0,last=0,lo=INT64_MAX,hi=INT64_MIN,count=0;
        while ((ret=pcap_next_ex(stream,&h,&bytes))==1) {
            int64_t stamp=(int64_t)h->ts.tv_sec*1000000+h->ts.tv_usec;
            if (count++==0) first=stamp;
            if (stamp<lo) lo=stamp;
            if (stamp>hi) hi=stamp;
            last=stamp;
        }
        if (ret!=-2) {fprintf(stderr,"%s\n",pcap_geterr(stream));return 2;}
        printf("%s\t%" PRId64 "\t%" PRId64 "\t%" PRId64 "\t%" PRId64 "\t%" PRId64 "\n",argv[i],count,first,last,lo,hi);
        pcap_close(stream);
    }
    return 0;
}
