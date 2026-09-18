#![allow(non_snake_case, non_upper_case_globals, unused_parens, unused_imports,
unused_variables, unused_mut, unused_assignments, dead_code)]
mod og;
use og::*;
use og::dataview_uniqDef::*;

fn main() {
    unsafe {
        og_startup();
        let mut toto: asn1SccMy_OctStr = std::mem::zeroed();
        go(&mut toto);
    }
}
