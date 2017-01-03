with SimpleTypes;
with Generic_Basic;
with Interfaces;
use Interfaces;

generic
    Min: Interfaces.Integer_64;
    Max: Interfaces.Integer_64;
package Generic_Integer is
    function Elem_Init return Interfaces.Integer_64 is (Min);
    function Has_Elem(Value: Interfaces.Integer_64) return Boolean is
        (Value <= Max);
    function Elem_First return Interfaces.Integer_64 is (Min);
    function Elem_Next(Value: Interfaces.Integer_64) return Interfaces.Integer_64 is
        (Value + 1);

    package Integer_type is new SimpleTypes(Element    => Interfaces.Integer_64,
                                            Elem_Init  => Elem_Init,
                                            Has_Elem   => Has_Elem,
                                            Elem_First => Elem_First,
                                            Elem_Next  => Elem_Next);

    package It is new Generic_Basic (P => Integer_type);

    subtype Instance is It.Basic_ASN1_Iterator;
end;
