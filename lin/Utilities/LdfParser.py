#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-lin project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


from enum import Enum, IntEnum

class LdfParsingState(IntEnum):

    Header = 1
    Nodes = 2
    Signals = 3
    DiagnosticSignals = 4
    Frames = 5
    DiagnosticFrames = 6
    NodeAttributes = 7
    ScheduleTables = 8
    SignalEncodingTypes = 9
    SignalRepresentation = 10
    EOF = 11


class LdfFile(object):

    ##
    # @brief pads out an array with a fill value
    def __init__(self, filename=None):

        self.ldfDictionary = {}
        self.ldfFile = open(filename, 'r')
        parsingState = LdfParsingState.Header
        self.linecount = 0  # ... using this to track file line number for error reporting purposes

        nextAddress = None

        currentBlock = None
        baseAddress = 0

        self.__sendChunksize = None

        while parsingState != LdfParsingState.EOF:
            if parsingState == LdfParsingState.Header:
                self.ldfDictionary['Header'], parsingState  = self.__parseLdfHeader()
            elif parsingState == LdfParsingState.Nodes:
                self.ldfDictionary['Nodes'], parsingState = self.__parseLdfNodes()
            elif parsingState == LdfParsingState.Signals:
                self.ldfDictionary['Signals'], parsingState = self.__parseLdfSignals()
            elif parsingState == LdfParsingState.DiagnosticSignals:
                self.ldfDictionary['DiagnosticSignals'], parsingState = self.__parseLdfDiagnosticSignals()
            elif parsingState == LdfParsingState.Frames:
                self.ldfDictionary['Frames'], parsingState = self.__parseLdfFrames()
            elif parsingState == LdfParsingState.DiagnosticFrames:
                self.ldfDictionary['DiagnosticFrames'], parsingState = self.__parseLdfDiagnosticFrames()
            elif parsingState == LdfParsingState.NodeAttributes:
                self.ldfDictionary['NodeAttributes'], parsingState = self.__parseLdfNodeAttributes()
            elif parsingState == LdfParsingState.ScheduleTables:
                self.ldfDictionary['ScheduleTables'], parsingState = self.__parseLdfScheduleTables()
            elif parsingState == LdfParsingState.SignalEncodingTypes:
                self.ldfDictionary['SignalEncodingTypes'], parsingState = self.__parseLdfSignalEncodingTypes()
            elif parsingState == LdfParsingState.SignalRepresentation:
                self.ldfDictionary['SignalRepresentation'], parsingState = self.__parseLdfSignalRepresentation()

        # ... by this stage, the LDF file has been parsed and converted to an internal dictionary form. 
        # We can then expose the details as required via getter methods (e.g. compositing any elements required).

    ##
    # @brief stuff
    def __reportError(self,msg):
        print("error: {0} (at line number {1})".format(msg,self.linecount))

    ##
    # @brief gets the next line from the ldf file or returns None at the end of file
    def __getLine(self):
        # Keep skipping blank or comment lines until we either find an entry, or the end of file
        comment = False
        while True:
            line = self.ldfFile.readline()
            if line == "":
                return None # ... end of file
            line = line.strip()
            self.linecount += 1
            # Throw away any comments lines (either single lines or multi-line comments)...
            try:
                if line[:2] == '//' or (line[:2] == '/*' and line[-2:] == '*/'):
                    continue
                if line[:2] == '/*':
                    comment = True
                    continue
                if comment and line[-2:] == '*/':  # 
                    comment = False
                    continue
            except:
                pass
            if line != "": # ... throw away blank lines - only looking at the good ones
                if '//' in line: # ... and strip trailing comments
                    line,_,_ = line.partition('//')
                    line = line.strip()
                return line  # ... what's left is only genuine content that we're interested in processing

    ##
    # @brief converts int or hex string to int (stripping leading and/or trailing spaces).
    def __int_or_hex(self,string_value):
        try:  
            int_val = int(string_value.strip())     # ... value could legitimately be in either decimal ...
        except:
            int_val = int(string_value.strip(),16)  # ... or hex, so allow for trying both conversions from string
        return int_val

    ##
    # @brief converts int or real string to a numeric value (stripping leading and/or trailing spaces).
    def __int_or_real(self,string_value):
        if '.' in string_value:  
            value = float(string_value.strip())     # ... value could legitimately be either a float ...
        else:
            value = self.__int_or_hex(string_value)  # ... or an integer in some representation or other, so allowing for trying both conversions from string
        return value


    ##
    # @brief checks what state we're moving to when the ldf block changes.
    def __checkNewState(self,line):
        reported_error = False
        state = LdfParsingState.EOF
        while True:
            line_lower = line.lower()  # ... only used for case independent matching (i.e. convert and do everyhting in lower, but extractions are from the mixed-case version of the line)
            if line_lower == "nodes {":
                state = LdfParsingState.Nodes
            elif line_lower == "signals {":
                state = LdfParsingState.Signals
            elif line_lower == "diagnostic_signals {":
                state = LdfParsingState.DiagnosticSignals
            elif line_lower == "frames {":
                state = LdfParsingState.Frames
            elif line_lower == "diagnostic_frames {":
                state = LdfParsingState.DiagnosticFrames
            elif line_lower == "node_attributes {":
                state = LdfParsingState.NodeAttributes
            elif line_lower == "schedule_tables {":
                state = LdfParsingState.ScheduleTables
            elif line_lower == "signal_encoding_types {":
                state = LdfParsingState.SignalEncodingTypes
            elif line_lower == "signal_representation {":
                state = LdfParsingState.SignalRepresentation
            else:
                # Continuing past the error here, as we may not beed the missing info, e.g. we might only need the daignostic info which could be present ...
                if reported_error == False:
                    self.__reportError("Unknown entry detected in the ldf file: '{0}'".format(line))
                    reported_error = True  # ... we only need to report the problem once per method call, so suppress after the first
                line = self.__getLine()
                if line is None:
                   break
                continue  # ... skip the unknown entry but reading until we reach the start of a block we know (see list above)
            break				
        return state

    ##
    # @brief parses out the header entries from the ldf file
    def __parseLdfHeader(self):
        # The header must be at the top of the file. As all blank lines and comment lines are stripped out, then keep reading and processing
        # until we reach a block that is not part of the header (at which point we've either processed the header, or it's not there).
        header = {'LIN_protocol_version':None,'LIN_language_version':None,'LIN_speed':None}  # ... note: speed if present is always in kbps
        while True:
            line = self.__getLine()
            line_lower = line.lower()  # ... only used for case independent matching (i.e. convert and do everyhting in lower, but extractions are from the mixed-case version of the line)
            if line is None:
                state = LdfParsingState.EOF
                break
            elif "lin_description_file" in line_lower:
                pass
            elif "lin_protocol_version" in line_lower:
                _,_,version = line.partition('"')
                header['LIN_protocol_version'],_,_ = version.partition('"')
            elif "lin_language_version" in line_lower:
                _,_,version = line.partition('"')
                header['LIN_language_version'],_,_ = version.partition('"')
            elif "lin_speed" in line_lower:
                # Note: according to the spec, the speed is always in kbps, so the units specified after thenumeric part can potentially be ignored.
                # "This sets the nominal bit rate for the cluster. It shall be in the range of 1 to 20 kbit/sec-ond"
                _,_,speed = line.partition('=')
                speed = speed.strip()
                speed_kbps,_,units = speed.partition(' ')
                header['LIN_speed'] = float(speed_kbps)
            else:
                state = self.__checkNewState(line)
                break
			
        return (header,state)

    ##
    # @brief parses out the nodes entries from the ldf file
    def __parseLdfNodes(self):
        # As all blank lines and comment lines are stripped out, keep reading and processing
        # until we reach a block that is not part of the nodes section.
        nodes = {'Master': {'node_name': None, 'time_base': None, 'jitter': None}, 'Slaves': []}  # ... time and jitter are in ms
        while True:
            line = self.__getLine()
            if line is None:
                state = LdfParsingState.EOF
                break
            elif "master:" in line.lower():
                parts = line[7:-1].split(",") # ... remove "Master:" and trailing ";"
                nodes['Master']['node_name'] = parts[0].strip()
                nodes['Master']['time_base'] = int(parts[1].strip()[:-2])
                nodes['Master']['jitter']    = int(parts[2].strip()[:-2])
            elif "slaves:" in line.lower():
                parts = line[7:-1].split(",") # ... remove "Slaves:" and trailing ";"
                for part in parts:
                    nodes['Slaves'].append(part.strip())
            elif "}" in line:
                pass
            else:
                state = self.__checkNewState(line)
                break
			
        return (nodes,state)


    ##
    # @brief parses out the signals entries from the ldf file
    def __parseLdfSignals(self):
        # As all blank lines and comment lines are stripped out, keep reading and processing
        # until we reach a block that is not part of the signals section.
        signals = {}  # ... dictionary entries added in form '<signal name>': {'signal_size': None, 'initial_value': None, 'publisher': None, 'subscriber': None}
        while True:
            line = self.__getLine()
            if line is None:
                state = LdfParsingState.EOF
                break
            elif "}" in line:
                line = self.__getLine()
                if line is None:
                    state = LdfParsingState.EOF
                    break
                state = self.__checkNewState(line)
                break
            else:
                signal_name,_,signal_details = line.partition(": ")
                parts = signal_details[:-1].split(",") # ... remove trailing ";"
				
                signal = {'signal_size': None, 'initial_value': None, 'publisher': None, 'subscriber': None}
                signal['signal_size']   = int(parts[0].strip())   # ... bit (0..7), byte (8), integer (16), array (16..64)
                signal['initial_value'] = int(parts[1].strip())   # ... note: this is an int or int array - currently not handling an int array (TODO) !!!!!!!!!!!!!!!!!!!!!!!!!!!
                signal['publisher']     = parts[2].strip()
                signal['subscriber']    = parts[3].strip()
				
                signals[signal_name] = signal

        return (signals,state)


    ##
    # @brief parses out the diagnostic signal entries from the ldf file
    def __parseLdfDiagnosticSignals(self):
        # As all blank lines and comment lines are stripped out, keep reading and processing
        # until we reach a block that is not part of the diagnostic signals section.
        signals = {}  # ... dictionary entries added in form '<signal name>': {'signal_size': None, 'initial_value': None}
        while True:
            line = self.__getLine()
            if line is None:
                state = LdfParsingState.EOF
                break
            elif "}" in line:
                line = self.__getLine()
                if line is None:
                    state = LdfParsingState.EOF
                    break
                state = self.__checkNewState(line)
                break
            else:
                signal_name,_,signal_details = line.partition(": ")
                parts = signal_details[:-1].split(",") # ... remove trailing ";"
				
                signal = {'signal_size': None, 'initial_value': None}
                signal['signal_size']   = int(parts[0].strip())   # ... bit (0..7), byte (8), integer (16), array (16..64)
                signal['initial_value'] = int(parts[1].strip())   # ... note: this is an int or int array - currently not handling an int array (TODO) !!!!!!!!!!!!!!!!!!!!!!!!!!!
				
                signals[signal_name] = signal

        return (signals,state)


    ##
    # @brief parses out the frames entries from the ldf file
    def __parseLdfFrames(self):
        # As all blank lines and comment lines are stripped out, keep reading and processing
        # until we reach a block that is not part of the frames section.
        frames = {}  # ... dictionary entries added in form '<frame name>': {'signal_size': None, 'initial_value': None, ???: []}
        id_to_name = {} # ... inverse lookup in case it's required
        block_depth = 1  # ... used to track if dealing with an inner-block or the outer-block entry.
        frame_name = None
        while True:
            line = self.__getLine()
            if line is None:
                state = LdfParsingState.EOF
                break
            elif "}" in line:
                if block_depth == 1:
                    line = self.__getLine()
                    if line is None:
                        state = LdfParsingState.EOF
                        break
                    state = self.__checkNewState(line)
                    break
                block_depth = 1
            else:
                if block_depth == 1:
                    frame_name,_,frame_details = line.partition(": ")
                    parts = frame_details[:-1].split(",") # ... remove trailing "{"
				
                    frame = {'frame_id': None, 'publisher': None, 'frame_size': None, 'signals': []}
                    frame['frame_id']   = int(parts[0].strip())
                    frame['publisher'] = parts[1].strip()
                    frame['frame_size'] = int(parts[2].strip())

                    frames[frame_name] = frame
                    id_to_name[frame['frame_id']] = frame_name
                    block_depth = 2  # ... inner-block for signals within frame
                else: # ... block depth == 2 so dealing with an inner-block ...
                    parts = line[:-1].split(",") # ... remove trailing ";"
                    signal = {'signal_name': None, 'signal_offset': None}
                    signal['signal_name']   = parts[0].strip()
                    signal['signal_offset']   = int(parts[1].strip())

                    frames[frame_name]['signals'].append(signal)
			
        if frames != {}:
            frames['__id_to_name'] = id_to_name
        return (frames,state)


    ##
    # @brief parses out the diagnostic frames entries from the ldf file
    def __parseLdfDiagnosticFrames(self):
        # As all blank lines and comment lines are stripped out, keep reading and processing
        # until we reach a block that is not part of the frames section.
        frames = {}  # ... dictionary entries added in form '<frame name>': {'signal_size': None, 'initial_value': None, ???: []}
        id_to_name = {} # ... inverse lookup in case it's required
        block_depth = 1  # ... used to track if dealing with an inner-block or the outer-block entry.
        frame_name = None
        while True:
            line = self.__getLine()
            if line is None:
                state = LdfParsingState.EOF
                break
            elif "}" in line:
                if block_depth == 1:
                    line = self.__getLine()
                    if line is None:
                        state = LdfParsingState.EOF
                        break
                    state = self.__checkNewState(line)
                    break
                block_depth = 1
            else:
                if block_depth == 1:
                    frame_name,_,frame_details = line.partition(": ")
                    frame_id = frame_details[:-1].strip() # ... remove trailing "{"
				
                    frame = {'frame_id': None, 'signals': []}
                    frame['frame_id'] = self.__int_or_hex(frame_id)
				    
                    frames[frame_name] = frame
                    id_to_name[frame['frame_id']] = frame_name
                    block_depth = 2  # ... inner-block for signals within frame
                else: # ... block depth == 2 so dealing with an inner-block ...
                    parts = line[:-1].split(",") # ... remove trailing ";"
                    signal = {'signal_name': None, 'signal_offset': None}
                    signal['signal_name']   = parts[0].strip()
                    signal['signal_offset']   = int(parts[1].strip())

                    frames[frame_name]['signals'].append(signal)
			
        if frames != {}:
            frames['__id_to_name'] = id_to_name
        return (frames,state)



    ##
    # @brief parses out the nodes attributes entries from the ldf file
    def __parseLdfNodeAttributes(self):
        # As all blank lines and comment lines are stripped out, keep reading and processing
        # until we reach a block that is not part of the frames section.
        node_attributes = {}  # ... dictionary entries added in form '<frame name>': {'signal_size': None, 'initial_value': None, ???: []}
        id_to_name = {} # ... inverse lookup in case it's required
        block_depth = 1  # ... used to track if dealing with an inner-block or the outer-block entry.
        node_name = None
        node_attribute_details = None
		
        while True:
            line = self.__getLine()
            if line is None:
                state = LdfParsingState.EOF
                break
            elif "}" in line:
                if block_depth == 1:
                    line = self.__getLine()
                    if line is None:
                        state = LdfParsingState.EOF
                        break
                    state = self.__checkNewState(line)
                    break
                block_depth -= 1
                if block_depth == 1:  # ... and clear for next entry
                    node_attribute_details = None
            else:
                if block_depth == 1:
                    node_attribute_details = {'LIN_protocol': None, 'configured_NAD': None, 'initial_NAD': None, 'product_id': None, 'response_error': None, 'N_As_timeout': None, 'N_Cr_timeout': None, 'configurable_frames': []}
                    node_name = line[:-1].strip() # ... remove trailing "{"
                    node_attributes[node_name] = node_attribute_details
                    block_depth = 2  # ... after current line changing to processing inner-block for node details

                elif block_depth == 2: # ... dealing with the node details

                    # Small utility function only needed for this block, to process value extraction ...
                    def __extract_value(equals_str):
                        value = None
                        _,_,value_str = equals_str[:-1].partition("=")  # ... ignore everyhting before the equals and strip off the trailing ";"
                        value_str = value_str.strip()
                        if '"' in value_str:
                            value = value_str[1:-1]
                        elif ',' in value_str:
                            parts = value_str.split(',')
                            value = [self.__int_or_hex(id_element) for id_element in parts]
                        elif 'ms' in value_str:
                            value = self.__int_or_hex(value_str[:-2])
                        elif 'ms' in value_str:
                            value = self.__int_or_hex(value_str[:-2])
                        elif value_str[0:1].isdigit():
                            value = self.__int_or_hex(value_str)
                        else:
                            value = value_str
                        return value

                    line_lower = line.lower()  # ... only used for case independent matching (i.e. convert and do everyhting in lower, but extractions are from the mixed-case version of the line)
                    if line[-1:] == "{":
                        block_depth = 3  # ... after current line changing to processing inner-block for configurable frames within node
                    elif 'lin_protocol' in line_lower: 
                        node_attributes[node_name]['LIN_protocol'] = __extract_value(line)
                    elif 'configured_nad' in line_lower:
                        node_attributes[node_name]['configured_NAD'] = __extract_value(line)
                    elif 'initial_nad' in line_lower:
                        node_attributes[node_name]['initial_NAD'] = __extract_value(line)
                    elif 'product_id' in line_lower:
                        node_attributes[node_name]['product_id'] = __extract_value(line)
                    elif 'response_error' in line_lower:
                        node_attributes[node_name]['response_error'] = __extract_value(line)
                    elif 'n_as_timeout' in line_lower:
                        node_attributes[node_name]['N_As_timeout'] = __extract_value(line)
                    elif 'n_cr_timeout' in line_lower:
                        node_attributes[node_name]['N_Cr_timeout'] = __extract_value(line)

                else: # ... block depth == 3 so dealing with an inner-block ...
                    configurable_frame = line[:-1].strip() # ... remove trailing ";"
                    node_attributes[node_name]['configurable_frames'].append(configurable_frame)

        return (node_attributes,state)



    ##
    # @brief parses out the schedule table entries from the ldf file
    def __parseLdfScheduleTables(self):
        # As all blank lines and comment lines are stripped out, keep reading and processing
        # until we reach a block that is not part of the frames section.
        schedule_tables = {}  # ... dictionary entries added in form '<frame name>': {'signal_size': None, 'initial_value': None, ???: []}
        block_depth = 1  # ... used to track if dealing with an inner-block or the outer-block entry.
        table_name = None
        while True:
            line = self.__getLine()
            if line is None:
                state = LdfParsingState.EOF
                break
            elif "}" in line:
                if block_depth == 1:
                    line = self.__getLine()
                    if line is None:
                        state = LdfParsingState.EOF
                        break
                    state = self.__checkNewState(line)
                    break
                block_depth = 1
            else:
                if block_depth == 1:
                    table_name = line[:-1].strip() # ... remove trailing "{"
                    schedule_tables[table_name] = []
                    block_depth = 2  # ... inner-block for signals within frame
                else: # ... block depth == 2 so dealing with an inner-block ...
                    command_name,_,frame_time = line[:-1].partition("delay") # ... remove trailing ";"
                    command = {'command': None, 'frame_time': None}
                    command['command']   = command_name.strip()
                    command['frame_time']   = int(frame_time.strip()[:-2].strip())

                    schedule_tables[table_name].append(command)
			
        return (schedule_tables,state)

		

    ##
    # @brief parses out the encoding types entries from the ldf file
    def __parseLdfSignalEncodingTypes(self):
        # As all blank lines and comment lines are stripped out, keep reading and processing
        # until we reach a block that is not part of the frames section.
        encoding_types = {}  # ... dictionary entries added in form '<frame name>': {'signal_size': None, 'initial_value': None, ???: []}
        id_to_name = {} # ... inverse lookup in case it's required
        block_depth = 1  # ... used to track if dealing with an inner-block or the outer-block entry.
        encoding_name = None
        while True:
            line = self.__getLine()
            if line is None:
                state = LdfParsingState.EOF
                break
            elif "}" in line:
                if block_depth == 1:
                    line = self.__getLine()
                    if line is None:
                        state = LdfParsingState.EOF
                        break
                    state = self.__checkNewState(line)
                    break
                block_depth = 1
            else:
                if block_depth == 1:
                    encoding_name = line[:-1].strip() # ... remove trailing "{"
                    encoding_types[encoding_name] = []
                    block_depth = 2  # ... inner-block for signals within frame
                else: # ... block depth == 2 so dealing with an inner-block ...
                    parts = line[:-1].split(",") # ... remove trailing ";"
                    encoding = {'value_type': None}

                    if 'logical_value' in parts[0].lower():
                        encoding = {'value_type': 'logical_value', 'signal_value': None, 'text_info': None}
                        encoding['signal_value']   = int(parts[1].strip())
                        if len(parts) == 3:
                            encoding['text_info']   = parts[2].strip()[1:-1]					
                    elif 'physical_value' in parts[0].lower():
                        encoding = {'value_type': 'physical_value', 'min_value': None, 'max_value': None, 'scale': None, 'offset': None, 'text_info': None}
                        encoding['min_value']   = int(parts[1].strip())
                        encoding['max_value']   = int(parts[2].strip())
                        encoding['scale']   = self.__int_or_real(parts[3].strip())
                        encoding['offset']   = self.__int_or_real(parts[4].strip())
                        if len(parts) == 6:
                            encoding['text_info']   = parts[5].strip()[1:-1]						
                    elif 'bcd_value' in parts[0].lower():
                        encoding = {'value_type': 'bcd_value'}
                    elif 'ascii_value' in parts[0].lower():
                        encoding = {'value_type': 'ascii_value'}

                    encoding_types[encoding_name].append(encoding)

        return (encoding_types,state)


    ##
    # @brief parses out the signal representations entries from the ldf file
    def __parseLdfSignalRepresentation(self):
        # As all blank lines and comment lines are stripped out, keep reading and processing
        # until we reach a block that is not part of the signals section.
        signal_representations = {}  # ... dictionary entries added in form '<signal name>': {'signal_size': None, 'initial_value': None, 'publisher': None, 'subscriber': None}
        signal_to_representation = {} # ... inverse lookup in case it's required
        while True:
            line = self.__getLine()
            if line is None:
                state = LdfParsingState.EOF
                break
            elif "}" in line:
                line = self.__getLine()
                if line is None:
                    state = LdfParsingState.EOF
                    break
                state = self.__checkNewState(line)
                break
            else:
                representation,_,signal_list = line.partition(": ")
                signal_list = signal_list[:-1].split(",") # ... remove trailing ";"
                signal_representations[representation] = []
                for entry in signal_list:
                    signal = entry.strip()
                    signal_representations[representation].append(signal)
                    signal_to_representation[signal] = representation

        if signal_representations != {}:
            signal_representations['__signal_to_representation'] = signal_to_representation	
        return (signal_representations,state)

    # Exposing the dictionary for test purposes - this will be replaced by appropriate getters.		
    def getLdfDictionary(self):
        return self.ldfDictionary
		createNode("nodename")
		by slave name require
		- list of signals
		- set of frames assicated with it
		- tx is slave to master
		- rx master to slave
		
		- event frames and collisions need to be looked at
		
		- list of slave object or a master object

if __name__ == "__main__":

    ldfFile = LdfFile("../../test/unitTest/Python_LIN_testLDF.ldf")

    print("\n\n")
    print("Ldf Header:")
    print(ldfFile.getLdfDictionary()['Header'])
    print("\n")
    print("Nodes:")
    print(ldfFile.getLdfDictionary()['Nodes'])
    print("\n")
    print("Signals:")
    print(ldfFile.getLdfDictionary()['Signals'])
    print("\n")
    print("DiagnosticSignals:")
    print(ldfFile.getLdfDictionary()['DiagnosticSignals'])
    print("\n")
    print("Frames:")
    print(ldfFile.getLdfDictionary()['Frames'])
    print("\n")
    print("DiagnosticFrames:")
    print(ldfFile.getLdfDictionary()['DiagnosticFrames'])
    print("\n")
    print("NodeAttributes:")
    print(ldfFile.getLdfDictionary()['NodeAttributes'])
    print("\n")
    print("ScheduleTables:")
    print(ldfFile.getLdfDictionary()['ScheduleTables'])
    print("\n")
    print("SignalEncodingTypes:")
    print(ldfFile.getLdfDictionary()['SignalEncodingTypes'])
    print("\n")
    print("SignalRepresentation:")
    print(ldfFile.getLdfDictionary()['SignalRepresentation'])
    print("\n")

