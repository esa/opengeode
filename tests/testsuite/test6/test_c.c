#include <signal.h>
#include "dataview-uniq.h"
void result_data(long long *val)
{
    printf("[C] result_data: %lld\n", *val);
}

volatile sig_atomic_t keep_going = 1;
void timer_expired()
{
    mytimer();
    keep_going = 0;
}

void SET_mytimer(asn1SccT_Int32 *val)
{
    printf("[C] SET MyTimer: %d\n", *val);
    alarm(((int)*val) / 1000);

}

int main()
{
    asn1SccT_Int32 test = 5;
    signal(SIGALRM, timer_expired);

    printf("[C Code] Running test\n");
    CInit();
    runTransition(0);
    start_something(&test);
    while (keep_going);    
    return 0;
}

