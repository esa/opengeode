#include <signal.h>
#include "dataview-uniq.h"

volatile sig_atomic_t keep_going = 1;

void myfunction_RI_result_data(long long *val)
{
    printf("[C] result_data: %lld\n", *val);
}

void myfunction_RI_SET_myTimer(asn1SccT_Int32 *val)
{
    printf("[C] SET MyTimer: %lld\n", *val);
    alarm(((int)*val) / 1000);

}

void timer_expired()
{
    myfunction_PI_myTimer();
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
    myfunction_initStates();
	
    printf("[C Code] Running test\n");
    myfunction_PI_start_something(&test);
    while (keep_going);    
    return 0;
}

