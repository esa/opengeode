--  This file was generated automatically by TASTE: DO NOT EDIT

package body ASN1_Iterators.iterators is

    --  ASN.1 File dataview-uniq.asn
    --  Module TASTE_BasicTypes
    package body T_Int_pkg is
        procedure To_ASN1(from: Interfaces.Integer_64; to: out ASN1_Type) is
        begin
            to := from;
        end;
    end;
    package body T_SeqOf_pkg is
        procedure To_ASN1(from: Inner.MySeqOf; to: out ASN1_Type) is
        begin
            for idx in 1..from.length loop
                to.data(idx) := from.data(idx);
            end loop;
            to.length := from.length;
        end;
    end;

end;