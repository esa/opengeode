#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "dataview-uniq.h"
#include "complexsdl.h"

static int counts[5] = {0};

void complexsdl_RI_response(asn1SccMyInteger * response_param)
{
    int val = (int)*response_param;
    printf("[C] response: %d\n", val);
    if (val < 1 || val > 4) {
        printf("Error: response value out of bounds: %d\n", val);
        exit(1);
    }
    counts[val]++;
}

int main()
{
    asn1SccMyInteger input_val = 42;
    int i;
    
    printf("[C Code] Running test\n");
    
    // Seed the random number generator
    srand(time(NULL));
    
    complexsdl_startup();
    
    for (i = 0; i < 10; i++) {
        complexsdl_PI_impulse(&input_val);
    }
    
    // Check that it is not 10 times the same
    for (i = 1; i <= 4; i++) {
        if (counts[i] == 10) {
            printf("Error: All 10 responses were identical: %d\n", i);
            exit(1);
        }
    }
    
    printf("C test completed successfully\n");
    return 0;
}
