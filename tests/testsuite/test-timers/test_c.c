#include "dataview.h"
#include <stdio.h>
#include <unistd.h>

extern void CInittest();
extern void test_PI_blah();

void test_RI_SET_toto(const asn1SccT_UInt32 * val)
{
    usleep(*val);
}

void test_RI_RESET_toto()
{

}

int main()
{
    CInittest();

    printf("hello\n");
    test_PI_blah();

    return 0;
}