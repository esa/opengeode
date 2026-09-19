#![allow(non_snake_case, non_upper_case_globals, unused_parens, unused_imports,
unused_variables, unused_mut, unused_assignments, dead_code)]
mod og;
use og::*;
use og::og_type::dataview_uniqDef::*;

fn main() {
    unsafe {
        og_startup();
        let mut toto: asn1SccMy_OctStr = test_string;
        // The Rust dataview keeps the full SIZE(0..20) for My-OctStr, so
        // "hello" (padded to n_count = 20) never equals 'hello' here:
        // every go() call takes the FALSE branch in state Wait and raises
        // the rezult RI once. The expected file has a single RI call, so
        // call go() once (test_ada.c/test_c.c call it three times because
        // their dataview uses n_count = 5, making go() #1 match 'hello').
        go(&mut toto);
    }
}
