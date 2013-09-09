<?xml version="1.0" ?>
<spec version="1.0">
    <module name="rabbitmq" version="1.0" flags="optional" level="5" fs="squashfs">
    
        <requires name="erlang"/>
        
        <!--  rabbitmq-server ubuntu package equivalent -->
        <var name="RabbitName" value="rabbitmq"/>
        
		<element source="/usr/lib/rabbitmq" type="dir" recurse="1" mask="*" />
		<element source="/var/lib/rabbitmq" type="dir" recurse="1" mask="*" />
		<element source="/usr/sbin/rabbitmqctl" />
		<element source="/usr/sbin/rabbitmq-server"/>
		<element source="/usr/sbin/rabbitmq-plugins" version="lts10.04" />
        <element source="/etc/rabbitmq" type="emptydir" />

		<!-- Add rc support -->
		<element source="/etc/init.d/rabbitmq-server" type="file" />
        
        <!-- logging -->
        <element source="/var/log/rabbitmq" type="emptydir" />
        <element source="/etc/logrotate.d/rabbitmq-server" />
        
        <script context="firstboot" rank="61">
            <![CDATA[
                groupadd -f ${RabbitName}
                egrep -q "^${RabbitName}:" /etc/passwd || (
                    useradd -M -d /var/lib/${RabbitName} -g ${RabbitName} --password x -c "Rabbitmq daemon" ${RabbitName}
                )  2>/dev/null 1>&2
                chown -R ${RabbitName}:${RabbitName} /var/log/${RabbitName}
                chown -R ${RabbitName}:${RabbitName} /var/lib/${RabbitName}
                if [ ! -d /$rimPrivData/rabbitmq ]
                then
                    chown -R ${RabbitName}:${RabbitName} /var/lib/${RabbitName}
                    mv /var/lib/rabbitmq /$rimPrivData/rabbitmq
                    ln -s /$rimPrivData/rabbitmq /var/lib/rabbitmq
                    chmod 400 /var/lib/${RabbitName}/.erlang.cookie
                fi
                return 0
             ]]>
        </script>
    </module>
</spec>
