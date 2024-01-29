#include "dataview.h"
#include "og.h"

// Provide the implementation of the Check_queue function
// The ada version is better as it is provided in the model
// but somehow the C backend does not propperly name the
// exported procedures
void og_check_queue(bool *res)
{
    *res = false;
}
int main(void)
{
   asn1SccBoolType val = true;
   og_startup();
   og_PI_saved_signal(&val);
   val = false;
   og_PI_saved_signal(&val);
   og_PI_run();   
}
