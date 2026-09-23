#![allow(non_snake_case, non_upper_case_globals, unused_parens, unused_imports,
unused_variables, unused_mut, unused_assignments, dead_code)]
use og::*;
use og::dataview_uniqDef::*;
fn main() {
    unsafe {
        og_startup();
        for_a();
        for_a();
        for_a();
        for_b();
        for_b();
        let mut param: asn1SccMyInteger = 1;
        reset_all(&mut param);
        reset_all(&mut param);
        exit_aggreg();
    }
}
