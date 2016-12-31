with SimpleTypes;
with Generic_Basic;

generic
    Min: Integer;
    Max: Integer;
package Generic_Integer is
    function Elem_Init return Integer is (Min);
    function Has_Elem (Value: Integer) return Boolean is (Value <= Max);
    function Elem_First return Integer is (Min);
    function Elem_Next (Value: Integer) return Integer is (Value + 1);

    package Integer_type is new SimpleTypes(Element    => Integer,
                                            Elem_Init  => Elem_Init,
                                            Has_Elem   => Has_Elem,
                                            Elem_First => Elem_First,
                                            Elem_Next  => Elem_Next);

    package It is new Generic_Basic (P => Integer_type);

    subtype Instance is It.Basic_ASN1_Iterator;
end;
