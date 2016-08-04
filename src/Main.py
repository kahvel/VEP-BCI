from connections.postoffice import MasterConnection, ConnectionPostOfficeEnd
import BCI
import PostOffice


if __name__ == "__main__":
    main_connection = ConnectionPostOfficeEnd.MainConnection()
    connections = MasterConnection.MasterConnection()
    bci_controller = BCI.BCI(connections, main_connection)
    PostOffice.PostOffice(main_connection, connections, bci_controller)
