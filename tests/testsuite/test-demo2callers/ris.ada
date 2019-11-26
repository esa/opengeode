with taste_dataview;
package ris is
    procedure AA(p: access taste_dataview.asn1SccMySeq) is null;
    pragma export(C, AA, "f1_RI_AA");
end ris;
