#include <stdio.h>

extern char *fixed_value();
extern int fixed_size();
int main()
{
    char * toto;
    int size;
    int i;
    printf("[C Code] Running test\n");
    CInit();
    runTransition(0);
    toto = fixed_value();
    size = fixed_size();
    printf("Size=%d\n", size);
    for (i = 0; i<size; i++) printf("%d", toto[i]);
    printf("\n");
    return 0;
}


