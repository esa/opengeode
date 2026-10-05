#![allow(non_snake_case, non_upper_case_globals, unused_parens, unused_imports,
unused_variables, unused_mut, unused_assignments, dead_code)]
mod toto;
use toto::*;
use toto::dataview_uniqDef::*;

fn main() {
    unsafe {
        toto_startup();
    }
}
