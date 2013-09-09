<?xml version="1.0" ?>
<spec version="1.0">
    <module name="erlang" version="1.0" flags="optional" level="5" fs="squashfs">
    
        <!-- ubuntu packages required :
            erlang-base 
            erlang-crypto 
            erlang-mnesia 
            erlang-os-mon 
            erlang-public-key 
            erlang-runtime-tools 
            erlang-snmp 
            erlang-ssl 
            erlang-syntax-tools 
        -->

        <element source="/usr/bin/epmd" />
        <element source="/usr/bin/erl" />
        <element source="/usr/bin/erl_call" />
        <element source="/usr/bin/erlc" />
        <element source="/usr/bin/escript" />
        <element source="/usr/bin/run_erl" />
        <element source="/usr/bin/start_embedded" />
        <element source="/usr/lib/erlang" type="dir" recurse="1" mask="*" />
    </module>
</spec>
