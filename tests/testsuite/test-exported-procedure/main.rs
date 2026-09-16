#![allow(non_snake_case, non_upper_case_globals, unused_parens, unused_imports,
unused_variables, unused_mut, unused_assignments, dead_code)]
mod og;
use og::*;
use og::dataview_uniqDef::*;

fn main() {
    unsafe {
        let mut p: asn1SccType2 = false;
        let mut t: asn1SccToto = asn1SccToto { elem_1: 42, elem_2: true };
        println!("{}", if !p { "OK" } else { "ERROR" });
        og_startup();
        og_PI_hehe(&mut t, &mut p);
        println!("{}", if p { "OK" } else { "ERROR" });
    }
}
