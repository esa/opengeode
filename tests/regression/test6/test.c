#include <math.h>
#include <stdio.h>

extern void adainit();


void myfunction_RI_result_data(long long *val)
{
    printf("[C] result_data: %lld\n", *val);
}

void myfunction_RI_set_mytimer(long long *val)
{
    printf("[C] SET MyTimer: %lld\n", *val);
}

void myfunction_RI_reset_mytimer()
{
    printf("RESET MyTimer\n");
}

int main()
{
    printf("[C Code] Running test\n");
    adainit();
    
    return 0;
}

