#![allow(non_snake_case, non_upper_case_globals, unused_parens, unused_imports,
unused_variables, unused_mut, unused_assignments, dead_code)]
mod complexsdl;
use complexsdl::*;
use complexsdl::dataview_uniqDef::*;

fn main() {
    unsafe {
        let mut x: asn1SccMyInteger = 0;
        complexsdl_startup();
        impulse(&mut x);
        impulse(&mut x);
    }
}
