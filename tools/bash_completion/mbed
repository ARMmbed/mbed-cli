# Based on mbed auto complete scripts

__mbedcomp_words_include() {
    local i=1
    while [[ "$i" -lt "$COMP_CWORD" ]]
    do
        if [[ "${COMP_WORDS[i]}" = "$1" ]]
        then
            return 0
        fi
            i="$((++i))"
    done
    return 1
}

# Find the previous non-switch word
__mbedcomp_prev() {
    local idx="$((COMP_CWORD - 1))"
    local prv="${COMP_WORDS[idx]}"
    while [[ "$prv" = -* ]]
    do
        idx="$((--idx))"
        prv="${COMP_WORDS[idx]}"
    done
    echo "$prv"
}

__mbedcomp() {
# break $1 on space, tab, and newline characters,
# and turn it into a newline separated list of words
    local list s sep=$'\n' IFS=$' '$'\t'$'\n'
    local cur="${COMP_WORDS[COMP_CWORD]}"

    for s in $1
    do
        __mbedcomp_words_include "$s" && continue
        list="$list$s$sep"
    done

    IFS="$sep"
    COMPREPLY=($(compgen -W "$list" -- "$cur"))
}

__mbed_complete_new() {
    
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    case "$cur" in 
        --*)
            __mbedcomp "
                --help
                --scm
                --program
                --library
                --mbedlib
                --create-only
                --depth
                --protocol
                --verbose
                --very_verbose
                "

            return
            ;;
        -*)
            __mbedcomp "
                -h
                -v
                -vv
                "
            return
            ;;
    esac
    case "$prev" in 
        --scm)
            __mbedcomp "bld git hg"
            return
            ;;
        --protocol)
            __mbedcomp "https http ssh git"
            return
            ;;
    esac
}

__mbed_complete_import() {
    
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    case "$cur" in 
        --*)
            __mbedcomp "
                --help
                --ignore
                --depth
                --protocol
                --verbose
                --very_verbose
                "

            return
            ;;
        -*)
            __mbedcomp "
                -h
                -I
                -v
                -vv
                "
            return
            ;;
    esac
    case "$prev" in 
        --protocol)
            __mbedcomp "https http ssh git"
            return
            ;;
    esac
}

__mbed_complete_add() {
    
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    case "$cur" in 
        --*)
            __mbedcomp "
                --help
                --ignore
                --depth
                --protocol
                --verbose
                --very_verbose
                "

            return
            ;;
        -*)
            __mbedcomp "
                -h
                -I
                -v
                -vv
                "
            return
            ;;
    esac
    case "$prev" in 
        --protocol)
            __mbedcomp "https http ssh git"
            return
            ;;
    esac
}

__mbed_complete_remove() {
    
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    case "$cur" in 
        --*)
            __mbedcomp "
                --help
                --verbose
                --very_verbose
                "

            return
            ;;
        -*)
            __mbedcomp "
                -h
                -v
                -vv
                "
            return
            ;;
    esac
}

__mbed_complete_deploy() {
    
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    case "$cur" in 
        --*)
            __mbedcomp "
                --help
                --ignore
                --depth
                --protocol
                --verbose
                --very_verbose
                "

            return
            ;;
        -*)
            __mbedcomp "
                -h
                -I
                -v
                -vv
                "
            return
            ;;
    esac
    case "$prev" in 
        --protocol)
            __mbedcomp "https http ssh git"
            return
            ;;
    esac
}

__mbed_complete_publish() {
    
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    case "$cur" in 
        --*)
            __mbedcomp "
                --help
                --all
                --message
                --verbose
                --very_verbose
                "

            return
            ;;
        -*)
            __mbedcomp "
                -h
                -A
                -M
                -v
                -vv
                "
            return
            ;;
    esac
}

__mbed_complete_update() {
    
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    case "$cur" in 
        --*)
            __mbedcomp "
                --help
                --clean
                --clean-files
                --clean-deps
                --ignore
                --depth
                --protocol
                --verbose
                --very_verbose
                "

            return
            ;;
        -*)
            __mbedcomp "
                -h
                -C
                -I
                -v
                -vv
                "
            return
            ;;
    esac
    case "$prev" in 
        --protocol)
            __mbedcomp "https http ssh git"
            return
            ;;
    esac
}

__mbed_complete_sync() {
    
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    case "$cur" in 
        --*)
            __mbedcomp "
                --help
                --verbose
                --very_verbose
                "

            return
            ;;
        -*)
            __mbedcomp "
                -h
                -v
                -vv
                "
            return
            ;;
    esac
}

__mbed_complete_ls() {
    
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    case "$cur" in 
        --*)
            __mbedcomp "
                --help
                --all
                --ignore
                --verbose
                --very_verbose
                "

            return
            ;;
        -*)
            __mbedcomp "
                -h
                -a
                -I
                -v
                -vv
                "
            return
            ;;
    esac
}

__mbed_complete_status() {
    
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    case "$cur" in 
        --*)
            __mbedcomp "
                --help
                --ignore
                --verbose
                --very_verbose
                "

            return
            ;;
        -*)
            __mbedcomp "
                -h
                -I
                -v
                -vv
                "
            return
            ;;
    esac
}

__mbed_complete_compile () {
    
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    case "$cur" in 
        --*)
            __mbedcomp "
                --help
                --toolchain
                --target
                --profile
                --library
                --config
                --prefix
                --source
                --build
                --clean
                --artifact-name
                --supported
                --app-config
                --verbose
                --very_verbose
                "

            return
            ;;
        -*)
            __mbedcomp "
                -h
                -t
                -m
                -c
                -N
                -S
                -v
                -vv
                "
            return
            ;;
    esac
    case "$prev" in 
        --target|-m)
            declare TARGETS=$(mbed target --supported | cut -d '|' -f 2 | sed -n '/^+/!p' | sed -n '/^Supported/!p' | sed -n '/^ [A-Z][A-Z]/p')
            __mbedcomp "${TARGETS}"
            return
            ;;
        --toolchain|-t)
            declare TOOLCHAINS=$(mbed target --supported | head -n 2 | tail -n 1 | tr '|' '\n' | sed -n '/^ Target/!p' | sed -n '/^ mbed/!p')
            __mbedcomp "${TOOLCHAINS}"
            return
            ;;
    esac
}

__mbed_complete_test() {
    
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    case "$cur" in 
        --*)
            __mbedcomp "
                --help
                --toolchain
                --target
                --compile-list
                --run-list
                --compile
                --run
                --tests-by-name
                --source
                --build
                --profile
                --clean
                --test-spec
                --app-config
                --verbose
                --very_verbose
                "

            return
            ;;
        -*)
            __mbedcomp "
                -h
                -t
                -m
                -n
                -c
                -v
                -vv
                "
            return
            ;;
    esac
    case "$prev" in 
        --target|-m)
            declare TARGETS=$(mbed target --supported | cut -d '|' -f 2 | sed -n '/^+/!p' | sed -n '/^Supported/!p' | sed -n '/^ [A-Z][A-Z]/p')
            __mbedcomp "${TARGETS}"
            return
            ;;
        --toolchain|-t)
            declare TOOLCHAINS=$(mbed target --supported | head -n 2 | tail -n 1 | tr '|' '\n' | sed -n '/^ Target/!p' | sed -n '/^ mbed/!p')
            __mbedcomp "${TOOLCHAINS}"
            return
            ;;
    esac
}

__mbed_complete_export() {
    
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    case "$cur" in 
        --*)
            __mbedcomp "
                --help
                --ide
                --target
                --source
                --clean
                --supported
                --verbose
                --very_verbose
                "

            return
            ;;
        -*)
            __mbedcomp "
                -h
                -i
                -m
                -c
                -S
                -v
                -vv
                "
            return
            ;;
    esac
    case "$prev" in 
        --target|-m)
            declare TARGETS=$(mbed export --supported | cut -d '|' -f 2 | sed -n '/^+/!p' | sed -n '/^Platform/!p' | sed -n '/^Total/!p')
            __mbedcomp "${TARGETS}"
            return
            ;;
        --ide|-i)
            declare IDES=$(mbed export --supported | tail -n +1 | head -n 2 | tr '|' '\n' | sed -n '/^+/!p' | sed -n '/^ Platform/!p')
            __mbedcomp "${IDES}"
            return
            ;;
    esac
}

__mbed_complete_detect() {
    
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    case "$cur" in 
        --*)
            __mbedcomp "
                --help
                --verbose
                --very_verbose
                "

            return
            ;;
        -*)
            __mbedcomp "
                -h
                -v
                -vv
                "
            return
            ;;
    esac
}

__mbed_complete_config() {
    
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    case "$cur" in 
        --*)
            __mbedcomp "
                --help
                --global
                --unset
                --list
                --verbose
                --very_verbose
                "

            return
            ;;
        -*)
            __mbedcomp "
                -h
                -G
                -U
                -L
                -v
                -vv
                "
            return
            ;;
    esac
}

__mbed_complete_target() {
    
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    case "$cur" in 
        --*)
            __mbedcomp "
                --help
                --global
                --supported
                --verbose
                --very_verbose
                "

            return
            ;;
        -*)
            __mbedcomp "
                -h
                -G
                -S
                -v
                -vv
                "
            return
            ;;
    esac
    case "$prev" in 
        target|-G|--global|-v|--verbose|-vv|--very_verbose)
            declare TARGETS=$(mbed target --supported | cut -d '|' -f 2 | sed -n '/^+/!p' | sed -n '/^Supported/!p' | sed -n '/^ [A-Z][A-Z]/p')
            __mbedcomp "${TARGETS}"
            return
            ;;
    esac
}
__mbed_complete_toolchain() {
    
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    case "$cur" in 
        --*)
            __mbedcomp "
                --help
                --global
                --supported
                --verbose
                --very_verbose
                "

            return
            ;;
        -*)
            __mbedcomp "
                -h
                -G
                -S
                -v
                -vv
                "
            return
            ;;
    esac
    case "$prev" in 
        toolchain|-G|--global|-v|--verbose|-vv|--very_verbose)
            declare TOOLCHAINS=$(mbed target --supported | head -n 2 | tail -n 1 | tr '|' '\n' | sed -n '/^ Target/!p' | sed -n '/^ mbed/!p')
            __mbedcomp "${TOOLCHAINS}"
            return
            ;;
    esac
}

__mbed_complete_help() {
    
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    case "$cur" in 
        --*)
            __mbedcomp "
                --help
                --verbose
                --very_verbose
                "

            return
            ;;
        -*)
            __mbedcomp "
                -h
                -v
                -vv
                "
            return
            ;;
    esac
}

_mbed () {
    local i=1 cmd prev

    prev="${COMP_WORDS[COMP_CWORD-1]}"

# find the subcommand
     while [[ "$i" -lt "$COMP_CWORD" ]]
     do
         local s="${COMP_WORDS[i]}"
         case "$s" in 
             --*)
                 cmd="$s"
                 break
                 ;;
             -*)
                 ;;
             *)
                 cmd="$s"
                 break
                 ;;
         esac

         i="$((++i))"
     done

    # Handle the main command completions
    if [[ "$i" -eq "$COMP_CWORD" ]]
    then
    local cmds="
      --version  
       new      
       import     
       add        
       remove     
       deploy  
       publish    
       update  
       sync   
       ls         
       status     
       compile 
       test       
       export     
       detect  
       config     
       target     
       toolchain  
       help
       "

       __mbedcomp "${cmds}"
    fi

    # Each subcommand has a completion function based on the parent
    case "$cmd" in 
         new) __mbed_complete_new ;;
         import) __mbed_complete_import ;;
         add) __mbed_complete_add ;;
         remove) __mbed_complete_remove ;;
         deploy) __mbed_complete_deploy ;;
         publish) __mbed_complete_publish ;;
         update) __mbed_complete_update ;;
         sync) __mbed_complete_sync ;;
         ls) __mbed_complete_ls ;;
         status) __mbed_complete_status ;;
         compile) __mbed_complete_compile ;;
         test) __mbed_complete_test ;;
         export) __mbed_complete_export;;
         detect) __mbed_complete_detect ;;
         config) __mbed_complete_config ;;
         target) __mbed_complete_target ;;
         toolchain) __mbed_complete_toolchain ;;
         *) ;;
         esac

}

complete -o bashdefault -o default -F _mbed mbed
complete -o bashdefault -o default -F _mbed mbed-cli

