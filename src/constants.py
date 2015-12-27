MAIN_NOTEBOOK = "MainNotebook"

# Tab names
WINDOW_TAB = "Window"
PLOT_NOTEBOOK = "Plot"
TARGETS_NOTEBOOK = "Targets"
EXTRACTION_NOTEBOOK = "Extraction"
RESULTS_TAB = "Results"
TEST_TAB = "Test"
ROBOT_TAB = "Robot"
EMOTIV_TAB = "Emotiv"
TRAINING_TAB = "Train"

TARGETS_TAB = "Targets"
PLOT_TAB = "Plot"
EXTRACTION_TAB = "Extraction"

TARGETS_TAB_TAB = "TargetsTab"
PLOT_TAB_TAB = "PlotTab"
EXTRACTION_TAB_TAB = "ExtractionTab"

EXTRACTION_TAB_NOTEBOOK = "ExtractionTabNotebook"

# Extraction tab notebook tab names
EXTRACTION_TAB_HARMONICS_TAB = "Harmonics"
EXTRACTION_TAB_OPTIONS_TAB = "Options"

HARMONIC_WEIGHT = "Weight"
HARMONIC_DIFFERENCE = "Difference"

PSDA_METHOD_TAB = "PSDA"
CCA_METHOD_TAB = "CCA"

# Test tab buttons
TEST_TIME = "Time"
TEST_MIN = "Min"
TEST_MAX = "Max"
TEST_STANDBY = "Standby"
TEST_TARGET = "Test target"
TEST_UNLIMITED = "Unlimited"
TEST_NONE = "None"
TEST_RANDOM = "Random"
TEST_COLOR = "Color"

# Window tab buttons
WINDOW_WIDTH = "Width"
WINDOW_HEIGHT = "Height"
WINDOW_COLOR = "Color"
WINDOW_FREQ = "Freq"
WINDOW_REFRESH = "Refresh"
WINDOW_MONITOR = "Monitor"

# Result tab buttons
RESULT_SHOW_BUTTON = "Show"
RESULT_RESET_BUTTON = "Reset"
RESULT_SAVE_BUTTON = "Save"

# Training tab buttons
TRAINING_START = "Train"
TRAINING_RECORD = "Record"
TRAINING_SAVE_EEG = "Save EEG"
TRAINING_LOAD_EEG = "Load EEG"

# Training tab options menu
TRAINING_RECORD_NORMAL = "Normal"
TRAINING_RECORD_NEUTRAL = "Neutral"
TRAINING_RECORD_DISABLED = "Disabled"

TRAINING_RECORD_NAMES = (TRAINING_RECORD_DISABLED, TRAINING_RECORD_NORMAL, TRAINING_RECORD_NEUTRAL)

# Window function names
WINDOW_NONE = "None"
WINDOW_HANNING = "Hann"
WINDOW_HAMMING = "Hamming"
WINDOW_BLACKMAN = "Blackman"
WINDOW_KAISER = "Kaiser"
WINDOW_BARTLETT = "Bartlett"

WINDOW_FUNCTION_NAMES = (WINDOW_NONE, WINDOW_HANNING, WINDOW_HAMMING, WINDOW_BLACKMAN, WINDOW_KAISER, WINDOW_BARTLETT)

# Arguments for sgipy.signal.get_window()
# boxcar, triang, blackman, hamming, hann, bartlett, flattop, parzen,
# bohman, blackmanharris, nuttall, barthann, kaiser (needs beta), gaussian (needs std),
# general_gaussian (needs power, width), slepian (needs width), chebwin (needs attenuation)

SCIPY_WINDOW_HANNING = "hann"
SCIPY_WINDOW_HAMMING = "hamming"
SCIPY_WINDOW_BLACKMAN = "blackmanharris"
SCIPY_WINDOW_KAISER = "kaiser"
SCIPY_WINDOW_BARTLETT = "bartlett"

# Interpolation function names
INTERPOLATE_LINEAR = "Linear"
INTERPOLATE_NEAREST = "Nearest"
INTERPOLATE_ZERO = "Zero"
INTERPOLATE_SLINEAR = "Slinear"
INTERPOLATE_QUADRATIC = "Quadratic"
INTERPOLATE_CUBIC = "Cubic"
INTERPOLATE_BARYCENTRIC = "Barycentric"

INTERPOLATE_NAMES = (INTERPOLATE_LINEAR, INTERPOLATE_NEAREST, INTERPOLATE_ZERO, INTERPOLATE_SLINEAR, INTERPOLATE_QUADRATIC, INTERPOLATE_CUBIC, INTERPOLATE_BARYCENTRIC)

# Arguments for scipy.interpolate.interp1d
# linear, nearest, zero, slinear, quadratic, cubic

SCIPY_INTERPOLATE_LINEAR = "linear"
SCIPY_INTERPOLATE_NEAREST = "nearest"
SCIPY_INTERPOLATE_ZERO = "zero"
SCIPY_INTERPOLATE_SLINEAR = "slinear"
SCIPY_INTERPOLATE_QUADRATIC = "quadratic"
SCIPY_INTERPOLATE_CUBIC = "cubic"

# Plot and Extraction tab options frame buttons
OPTIONS_NORMALISE = "Normalise"
OPTIONS_DETREND = "Detrend"
OPTIONS_FILTER = "Filter"
OPTIONS_STEP = "Step"
OPTIONS_LENGTH = "Length"
OPTIONS_FROM = "From"
OPTIONS_TO = "To"
OPTIONS_TAPS = "Taps"
OPTIONS_ARG = "Arg"
OPTIONS_WINDOW = "Window"
OPTIONS_BREAK = "Break"
OPTIONS_INTERPOLATE = "Interp"

METHODS_FRAME = "Methods"

MAIN_FRAME = "MainFrame"
BOTTOM_FRAME = "BottomFrame"

PLUS_MINUS_FRAME = "PlusMinusFrame"
RADIOBUTTON_FRAME = "RadiobuttonFrame"
DISABLE_DELETE_FRAME = "DisableDeleteFrame"

TARGET_FRAME = "TargetFrame"
RESULT_FRAME = "ResultFrame"

# Color textbox's textbox name
TEXTBOX = "Textbox"

# Target tab buttons
TARGET_FREQ = "Freq"
TARGET_DELAY = "Delay"
TARGET_WIDTH = "Width"
TARGET_HEIGHT = "Height"
TARGET_COLOR1 = "Color1"
TARGET_X = "x"
TARGET_Y = "y"
TARGET_COLOR0 = "Color0"
TARGET_SEQUENCE = "Sequence"

# Detrend optionmenu
CONSTANT_DETREND = "Constant"
LINEAR_DETREND = "Linear"
NONE_DETREND = "None"

DETREND_NAMES = (LINEAR_DETREND, CONSTANT_DETREND, NONE_DETREND)

# Filter optionmenu
NONE_FILTER = "None"
LOWPASS_FILTER = "Low-pass"
HIGHPASS_FILTER = "High-pass"
BANDPASS_FILTER = "Band-pass"

FILTER_NAMES = (NONE_FILTER, LOWPASS_FILTER, HIGHPASS_FILTER, BANDPASS_FILTER)

# Plus minus frame buttons
PLUS = "+"
MINUS = " -"

# Disable and Delete frame buttons
DISABLE = "Disable"
DELETE = "Delete"

# Bottom frame buttons
START_BUTTON = "Start"
STOP_BUTTON = "Stop"
SAVE_BUTTON = "Save"
LOAD_BUTTON = "Load"
EXIT_BUTTON = "Exit"
SETUP_BUTTON = "Setup"

# Extraction method buttons
PSDA = "PSDA"
SUM_PSDA = "Sum PSDA"
CCA = "CCA"
BOTH = "Both"
SUM_BOTH = "Sum Both"

EXTRACTION_METHOD_NAMES = (PSDA, SUM_PSDA, CCA, BOTH, SUM_BOTH, "shortCCAPSDA")

# Plot type buttons
SIGNAL = "Signal"
SUM_SIGNAL = "Sum signal"
AVG_SIGNAL = "Avg signal"
SUM_AVG_SIGNAL = "Sum avg signal"
POWER = "Power"
SUM_POWER = "Sum power"
AVG_POWER = "Avg power"
SUM_AVG_POWER = "Sum avg power"

# Names of the classes
MULTIPLE_REGULAR = "MultipleRegular"
MULTIPLE_AVERAGE = "MultipleAverage"
SINGLE_REGULAR = "SingleRegular"
SINGLE_AVERAGE = "SingleAverage"

# Same tab notebook tab initial buttons
ALL_TAB = "All"
PLUS_TAB = "+"

SENSORS_FRAME = "Sensors"
OPTIONS_FRAME = "Options"

# Sensor names in Plot and Extraction tab
SENSORS = ("AF3", "F7", "F3", "FC5","T7", "P7", "O1", "O2", "P8", "T8", "FC6","F4", "F8", "AF4")

HEADSET_FREQ = 128

# Messages to PostOffice
START_MESSAGE = "Start"
STOP_MESSAGE = "Stop"
EXIT_MESSAGE = "Exit"
CLOSE_MESSAGE = "Close"
SETUP_MESSAGE = "Setup"
FAIL_MESSAGE = "Fail"
SUCCESS_MESSAGE = "Success"

SHOW_RESULTS_MESSAGE = "Show results"
RESET_RESULTS_MESSAGE = "Reset results"
SAVE_RESULTS_MESSAGE = "Save results"

SAVE_EEG_MESSAGE = "Save EEG"
LOAD_EEG_MESSAGE = "Load EEG"

# By default load values from this file
DEFAULT_FILE = "default.txt"

DATA_BACKGROUND = "Background"
DATA_TARGETS = "Targets"
DATA_FREQS = "Freqs"
DATA_PLOTS = "Plots"
DATA_EXTRACTION = "Extraction"
DATA_TEST = "Test"
DATA_HARMONICS = "Harmonics"
DATA_ROBOT = "Robot"
DATA_EMOTIV = "Emotiv"
DATA_TRAINING = "Training"

DATA_SENSORS = SENSORS_FRAME
DATA_OPTIONS = OPTIONS_FRAME
DATA_METHODS = METHODS_FRAME

DATA_METHOD = "Method"

DATA_FREQ = "Freq"

DATA_WEIGHTS = "Weights"

CONNECTION_EMOTIV = "Emotiv"
CONNECTION_PSYCHOPY = "Psychopy"
CONNECTION_ROBOT = "Robot"
CONNECTION_PLOT = "Plot"
CONNECTION_EXTRACTION = "Extraction"

CONNECTION_EMOTIV_NAME = "Emotiv"
CONNECTION_PSYCHOPY_NAME = "Psychopy"
CONNECTION_PLOT_NAME = "Plot"
CONNECTION_EXTRACTION_NAME = "Extraction"
CONNECTION_MAIN_NAME = "Main"
CONNECTION_ROBOT_NAME = "Robot"

RESULT_SUM = "Sum"

ROBOT_OPTION_FORWARD = "Forward"
ROBOT_OPTION_BACKWARD = "Backward"
ROBOT_OPTION_RIGHT = "Right"
ROBOT_OPTION_LEFT = "Left"
ROBOT_OPTION_STOP = "Stop"

MOVE_LEFT = "1"
MOVE_RIGHT = "2"
MOVE_FORWARD = "3"
MOVE_BACKWARD = "4"
MOVE_STOP = "0"

ROBOT_COMMANDS = (MOVE_BACKWARD, MOVE_FORWARD, MOVE_LEFT, MOVE_RIGHT, MOVE_STOP)

ROBOT_TEST = "Test"
ROBOT_NONE = "None"

ROBOT_STREAM = "Stream"
STREAM_X = "x"
STREAM_Y = "y"
STREAM_WIDTH = "Width"
STREAM_HEIGHT = "Height"
