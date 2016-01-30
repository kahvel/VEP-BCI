from connections.postoffice import MasterConnection, ConnectionPostOfficeEnd
import Recording
import Training
import PostOffice


if __name__ == "__main__":
    main_connection = ConnectionPostOfficeEnd.TrainingConnection()
    connections = MasterConnection.TrainingMasterConnection()
    recording = Recording.Recording()
    bci_controller = Training.Training(connections, main_connection, recording)
    PostOffice.PostOffice(main_connection, connections, bci_controller)
