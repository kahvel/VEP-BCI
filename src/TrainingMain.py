from connections.postoffice import MasterConnection, ConnectionPostOfficeEnd
import Training
import PostOffice


if __name__ == "__main__":
    main_connection = ConnectionPostOfficeEnd.TrainingConnection()
    connections = MasterConnection.TrainingMasterConnection()
    bci_controller = Training.Training(connections, main_connection)
    PostOffice.PostOffice(main_connection, connections, bci_controller)
