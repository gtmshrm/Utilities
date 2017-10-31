import tensorflow as tf
import json


class TF_DistributedServer:
    """Distributed trainer program.

    It implements between-graph-replication and asynchronous training.
    It includes code for parameter server and worker tasks.
    For more info, refer https://www.tensorflow.org/deploy/distributed

    Parameter server: Tasks involve storing weights, updating them, etc.
    Worker: Tasks involve pre-processing, loss calculation, backprop, etc.

    Run:
        - Machine A (with/without GPU):
            Run ps: python3 trainer.py, with the following changes in machines.json:
                job_name="ps", task_index="0"
            # Run worker (in other terminal) on machine A only if
            # it has GPU, else skip this step.
            Run worker: python3 trainer.py, with the following changes in machines.json:
                job_name="worker", task_index="0"
        - Machine B:
            Run worker: python3 trainer.py, with the following changes in machines.json:
                job_name="worker", task_index="1"
        - Machine C:
            Run worker: python3 trainer.py, with the following changes in machines.json:
                job_name="worker", task_index="2"

    Note:
        This trainer can train on any number of machines and also,
        gpu is not manditory for distributed training.
    """

    def __init__(self, machines_json, checkpoint_dir="/tmp/train_logs"):
        """

        Args:
            machines_json: A `str` json which contains all ps and worker hosts.
            checkpoint_dir: A `str` containing the path to checkpoint directory.
        """
        with open(machines_json) as json_file:
            hosts = json.load(json_file)
        self.ps_hosts = hosts['ps_hosts']
        self.worker_hosts = hosts['worker_hosts']
        self.job_name = hosts['job_name']
        self.task_index = int(hosts['task_index'])
        self.checkpoint_dir = checkpoint_dir
        # create a cluster from the parameter server and worker hosts
        self.cluster = tf.train.ClusterSpec({
                                "ps": self.ps_hosts,
                                "worker": self.worker_hosts})
        # create and start a server for the local task
        self.server = tf.train.Server(
                                self.cluster,
                                job_name=self.job_name,
                                task_index=self.task_index)

    def device_setter(self):
        """Assigns job to worker.

        Returns:
            A `tf.device` which sets job for worker on localhost.
        """
        return tf.device(tf.train.replica_device_setter(
                    worker_device="/job:worker/task:%d" % self.task_index,
                    cluster=self.cluster))

    def monitored_training_session(self):
        """Creates a `MonitoredSession` for training.

        Returns:
            A `tf.train.MonitoredTrainingSession` which runs monitored session.
        """
        return tf.train.MonitoredTrainingSession(
                    master=self.server.target,
                    is_chief=(self.task_index == 0),
                    checkpoint_dir=self.checkpoint_dir)


if __name__ == '__main__':
    TF_DistributedServer_Obj = TF_DistributedServer(
                                            machines_json='./machines.json',
                                            checkpoint_dir='/tmp/train_logs')

    if TF_DistributedServer_Obj.job_name == "ps":
        TF_DistributedServer_Obj.server.join()

    elif TF_DistributedServer_Obj.job_name == "worker":
        with TF_DistributedServer_Obj.device_setter():
            # ---------- BUILD MODEL HERE ----------
            print(">>>>>>>>>> BUILDING MODEL >>>>>>>>>>")
            x = tf.Variable(2, name='x', dtype=tf.float32)
            log_x = tf.log(x)
            loss = tf.square(log_x)

            global_step = tf.contrib.framework.get_or_create_global_step()

            train_op = tf.train.AdagradOptimizer(0.01).minimize(
                          loss, global_step=global_step)

        with TF_DistributedServer_Obj.monitored_training_session() as mon_sess:
            # ---------- RUN OPs HERE ----------
            print(">>>>>>>>>> RUNNING OPs >>>>>>>>>>")
            for i in range(10):
                print('Step {}...'.format(i))
                mon_sess.run(train_op)
