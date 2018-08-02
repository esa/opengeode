#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <mqueue.h>

#include "dataview-uniq.h"
#include "orchestrator_enums_def.h"
#include "queue_manager.h"

int OpenMsgQueueForReading(char *queueName)
{
    mqd_t queue_id;
    if (0 == open_exchange_queue_for_reading(queueName, &queue_id))
        return queue_id;
    return -1;
}

void CloseMsgQueue(int queue_id)
{
    mq_close(queue_id);
}

int GetMsgQueueBufferSize(int _queue_id)
{
    struct mq_attr mqstat;
    mq_getattr(_queue_id, &mqstat);
    return mqstat.mq_msgsize;
}

int RetrieveMessageFromQueue(int queue_id, int maxSize, byte *pBuf)
{
    int message_received_type = -1;
    retrieve_message_from_queue(queue_id, maxSize, pBuf, &message_received_type);
    return(message_received_type);
}

T_orchestrator_RI_list ii_pulse = i_pulse;
typedef struct {
    int tc_id;
    MyEnum pulse_param;
} pulse_TCDATA;

int SendTC_pulse(void *p_pulse_param)
{
    static mqd_t q = (mqd_t)-2;
    if (((mqd_t)-2) == q) {
        static char QName[1024];
        sprintf(QName, "%d_orchestrator_RI_queue", geteuid());
        open_exchange_queue_for_writing(QName, &q);
    }
    pulse_TCDATA data;
    data.tc_id = (int) i_pulse;
    data.pulse_param = * (MyEnum *) p_pulse_param;
    if (((mqd_t)-1) != q) {
        write_message_to_queue(q, sizeof(pulse_TCDATA)-4, &data.pulse_param, data.tc_id);
    } else {
        return -1;
    }
    return 0;
}
T_orchestrator_PI_list ii_telemetry = i_telemetry;
T_orchestrator_PI_list ii_peek_list = i_peek_list;
T_orchestrator_PI_list ii_peek_fixed = i_peek_fixed;
