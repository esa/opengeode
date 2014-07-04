#include <math.h>
#include <stdio.h>
#include <signal.h>
#include <stdlib.h>

extern void adainit();
extern void myfunction_start_something(long long *);
extern void myfunction_mytimer();

volatile sig_atomic_t keep_going = 1;

void myfunction_RI_result_data(long long *val)
{
    printf("[C] result_data: %lld\n", *val);
}

void myfunction_RI_set_mytimer(long long *val)
{
    printf("[C] SET MyTimer: %lld\n", *val);
    alarm(((int)*val) / 1000);

}

void timer_expired()
{
    myfunction_mytimer();
    keep_going = 0;
}


void myfunction_RI_reset_mytimer()
{
    printf("RESET MyTimer\n");
}

int main()
{
    long long test = 5;
    signal(SIGALRM, timer_expired);

    printf("[C Code] Running test\n");
    adainit();
    myfunction_start_something(&test);
    while (keep_going);    
    return 0;
}

