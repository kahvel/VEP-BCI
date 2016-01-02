from connections.postoffice import MasterConnection, ConnectionPostOfficeEnd
import Recording
import BCI
import PostOffice


if __name__ == "__main__":
    main_connection = ConnectionPostOfficeEnd.MainConnection()
    connections = MasterConnection.MasterConnection()
    recording = Recording.Recording()
    bci_controller = BCI.BCI(connections, main_connection, recording)
    PostOffice.PostOffice(main_connection, connections, bci_controller)
