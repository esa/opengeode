--  This file is a stub for the implementation of the required interfaces
--  It is normally overwritten by TASTE with the actual connection to the
--  middleware. If you use Opengeode independently from TASTE you must
--  edit the .adb (body) with your own implementation of these functions.
--  The body stub will be generated only once.

with DV;
use DV;
with adaasn1rtl;
use adaasn1rtl;

with Interfaces.C.Strings; use Interfaces.C.Strings;

package foo_RI is

   --  In TASTE, used to return the state as char * (but uses malloc so
   --  just return null here - feel free to implement it differently)
   function To_C_Pointer (State_As_String : String) return Chars_Ptr is
      (Null_Ptr);


procedure dummy is null;
end foo_RI;
