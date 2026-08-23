package body challenge_RI is
   procedure pow (a : in out asn1SccT_UInt32; b : in out asn1SccT_UInt32; res : out asn1SccT_UInt32) is
       procedure C_Pow (a : in out asn1SccT_UInt32; b : in out asn1SccT_UInt32; res : out asn1SccT_UInt32) with Import, Convention => C, Link_Name => "challenge_RI_pow";
   begin
       C_Pow (a,b, res);
   end pow;

end challenge_RI;
