#![allow(non_snake_case, non_upper_case_globals, unused_parens, unused_imports,
unused_variables, unused_mut, unused_assignments, dead_code)]
mod complexsdl;
use complexsdl::*;
use complexsdl::dataview_uniqDef::*;

fn main() {
    unsafe {
        complexsdl_startup();
        // Note: the Rust backend does not implement <proc>_state() yet
        // (it returns NULL), so it is not dereferenced here. The state-string
        // behaviour is asserted by the Ada and C binaries.
        tick();
        tick();
        tick();
    }
}
