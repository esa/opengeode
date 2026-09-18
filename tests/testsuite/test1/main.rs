#![allow(non_snake_case, non_upper_case_globals, unused_parens, unused_imports,
unused_variables, unused_mut, unused_assignments, dead_code)]
use og::*;
use og::dataview_uniqDef::*;
fn main() {
    unsafe {
        og_startup();
        let mut toto = test_string;
        go(&mut toto);
        go(&mut toto);
        go(&mut toto);
    }
}
