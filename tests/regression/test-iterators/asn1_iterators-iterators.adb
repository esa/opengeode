--  This file was generated automatically by TASTE: DO NOT EDIT

package body ASN1_Iterators.iterators is

    --  ASN.1 File dataview-uniq.asn
    --  Module TASTE_BasicTypes
    package body T_Int_pkg is
        function Image(Elm: ASN1_Type) return String is (Elm'Img);

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

        function Image(Elm: ASN1_Type) return String is
            (if Elm.Length > 0 then
                (Image(Elm.Data(1)) & (if Elm.Length > 1 then "," &
                     Image(ASN1_Type'(Length => Elm.Length-1,
                                      Data   => Elm.Data(2..Elm.Length) &
                                                Elm.Data(1..Elm.Data'Length-Elm.Length+1)))
                 else ""))
            else "");
    end;

end;