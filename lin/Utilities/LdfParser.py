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
    SporadicFrames = 7
    EventTriggeredFrames = 8
    NodeAttributes = 9
    ScheduleTables = 10
    SignalEncodingTypes = 11
    SignalRepresentation = 12
    EOF = 13


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

        try:
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
                elif parsingState == LdfParsingState.SporadicFrames:
                    self.ldfDictionary['SporadicFrames'], parsingState = self.__parseLdfSporadicFrames()
                elif parsingState == LdfParsingState.EventTriggeredFrames:
                    self.ldfDictionary['EventTriggeredFrames'], parsingState = self.__parseLdfEventTriggeredFrames()
                elif parsingState == LdfParsingState.NodeAttributes:
                    self.ldfDictionary['NodeAttributes'], parsingState = self.__parseLdfNodeAttributes()
                elif parsingState == LdfParsingState.ScheduleTables:
                    self.ldfDictionary['ScheduleTables'], parsingState = self.__parseLdfScheduleTables()
                elif parsingState == LdfParsingState.SignalEncodingTypes:
                    self.ldfDictionary['SignalEncodingTypes'], parsingState = self.__parseLdfSignalEncodingTypes()
                elif parsingState == LdfParsingState.SignalRepresentation:
                    self.ldfDictionary['SignalRepresentation'], parsingState = self.__parseLdfSignalRepresentation()
        except:
            self.__reportError("Untrapped exception detected in the LDF file")
            raise

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
            elif line_lower == "sporadic_frames {":
                state = LdfParsingState.SporadicFrames
            elif line_lower == "event_triggered_frames {":
                state = LdfParsingState.EventTriggeredFrames
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
            elif "}" == line:
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
            elif "}" == line:
                line = self.__getLine()
                if line is None:
                    state = LdfParsingState.EOF
                    break
                state = self.__checkNewState(line)
                break
            else:
                signal_name,_,signal_details = line.partition(": ") 
                parts = signal_details[:-1].split(",") # ... remove trailing ";"
				
                signal = {'signal_size': None, 'initial_value': [], 'publisher': None, 'subscribers': []}
                signal['signal_size'] = int(parts[0].strip())   # ... bit (0..7), byte (8), integer (16), array (16..64)
                i = 0
                if "{" in parts[1]:
                    while True:
                        i += 1
                        if "}" in parts[i]:
                            signal['initial_value'].append(int(parts[1].replace("{","").replace("}","").strip()))
                            break
                        signal['initial_value'].append(int(parts[1].replace("{","").replace("}","").strip()))							
                else:
                    signal['initial_value'] = [int(parts[1].strip())]
                    i = 2
                signal['publisher'] = parts[i].strip()
                signal['subscribers'] = [parts[s].strip() for s in range(i+1,len(parts))]	
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
            elif "}" == line:
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
            elif "}" == line:
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
            elif "}" == line:
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
    # @brief parses out the sporadic frames entries from the ldf file
    def __parseLdfSporadicFrames(self):
        # As all blank lines and comment lines are stripped out, keep reading and processing
        # until we reach a block that is not part of the frames section.
        sporadic_frames = {}  # ... dictionary entries added in form '<sporadic frame name>': [<frame_name list>]}
        while True:
            line = self.__getLine()
            if line is None:
                state = LdfParsingState.EOF
                break
            elif "}" == line:
                line = self.__getLine()
                if line is None:
                    state = LdfParsingState.EOF
                    break
                state = self.__checkNewState(line)
                break
            else:
                sporadic_frame_name,_,frame_list = line.partition(": ")
                frame_list = frame_list[:-1].split(",") # ... remove trailing ";"
                sporadic_frames[sporadic_frame_name] = [frame.strip() for frame in frame_list]

        return (sporadic_frames,state)


    ##
    # @brief parses out the event triggered frames entries from the ldf file
    def __parseLdfEventTriggeredFrames(self):
        # As all blank lines and comment lines are stripped out, keep reading and processing
        # until we reach a block that is not part of the frames section.
        et_frames = {}  # ... dictionary entries added in form '<frame name>': {'<event triggered frame name': 'collision_resolving_schedule_table': <table id>, 'frame_id': <frame_id>, 'frame_name': None}
        while True:
            line = self.__getLine()
            if line is None:
                state = LdfParsingState.EOF
                break
            elif "}" == line:
                line = self.__getLine()
                if line is None:
                    state = LdfParsingState.EOF
                    break
                state = self.__checkNewState(line)
                break
            else:
                et_frame_name,_,frame_details = line.partition(": ")
                parts = frame_details[:-1].split(",") # ... remove trailing ";"
                et_frame = {'collision_resolving_schedule_table': None, 'frame_id': None, 'frame_name': None}
				
                et_frame['collision_resolving_schedule_table']   = parts[0].strip()
                et_frame['frame_id']   = parts[1].strip()
                if len(parts) == 3:
                    et_frame['frame_name']   = int(parts[2].strip())

                et_frames[et_frame_name] = et_frame

        return (et_frames,state)


    ##
    # @brief parses out the nodes attributes entries from the ldf file
    def __parseLdfNodeAttributes(self):
        # As all blank lines and comment lines are stripped out, keep reading and processing
        # until we reach a block that is not part of the frames section.
        node_attributes = {}  # ... dictionary entries added in form '<frame name>': {'signal_size': None, 'initial_value': None, ???: []}
        block_depth = 1  # ... used to track if dealing with an inner-block or the outer-block entry.
        node_name = None
        node_attribute_details = None
		
        while True:
            line = self.__getLine()
            if line is None:
                state = LdfParsingState.EOF
                break
            elif "}" == line:
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
        schedule_tables = {'__diagnostic_table': None, '__diagnostic_index': None}  # ... dictionary entries added in form '<frame name>': {'signal_size': None, 'initial_value': None, ???: []}

        block_depth = 1  # ... used to track if dealing with an inner-block or the outer-block entry.
        table_name = None
        schedule_index = 0
        frame_delays = {}
        current_delay = None
        while True:
            line = self.__getLine()
            if line is None:
                state = LdfParsingState.EOF
                break
            elif "}" == line:
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
                    schedule_index += 1  # ... an arbitrary index for the schedules based on order of appearance in the LDF file (from 1 to 255 max - not enforced)
                    table_name = line[:-1].strip() # ... remove trailing "{"
                    schedule_tables[table_name] = {'index': schedule_index, 'frames': []}
                    block_depth = 2  # ... inner-block for signals within frame
                else: # ... block depth == 2 so dealing with an inner-block ...
                    command_entry,_,delay = line[:-1].partition("delay") # ... remove trailing ";"
                    command = {'type': None, 'SID': None, 'name': None, 'NAD': None, 'node': None, 'dump': None, 'free': None, 'frame_index': None,'delay': None}
                    current_delay = int(delay.strip()[:-2].strip())
                    command['delay'] = current_delay
					
                    # I've no examples as to how some of these are presented (ascii, hex, etc.), or for that matter how they're used, so changes will almost certainly be required (TODO)
                    command_lower = command_entry.lower()
                    if 'masterreq' in command_lower:
                        command['type'] = 'MasterReq'
                        schedule_tables['__diagnostic_table'] = table_name
                        schedule_tables['__diagnostic_index'] = schedule_index
                    elif 'slaveresp' in command_lower:
                        command['type'] = 'SlaveResp'
                    elif 'assignnad' in command_lower:
                        command['type'] = 'AssignNAD'
                        command['SID']= 0xB0                      
                        _,_,node_name = command_entry.strip()[:-1].partition("{")
                        command['node']= node_name.strip()                       
                    elif 'conditionalchangenad' in command_lower:
                        command['SID']= 0xB3                      
                        command['type'] = 'ConditionalChangeNAD'
                        _,_,nad_details = command_entry.strip()[:-1].partition("{")
                        parts = nad_details.split(",")
                        nad = {'NAD': None, 'id': None, 'byte': None, 'mask': None, 'inv': None, 'new_NAD': None}
                        nad['NAD'] = self.__int_or_hex(parts[0])  # ... these should all be hex values                 
                        nad['id'] = self.__int_or_hex(parts[1])               
                        nad['byte'] = self.__int_or_hex(parts[2])                      
                        nad['mask'] = self.__int_or_hex(parts[3])               
                        nad['inv'] = self.__int_or_hex(parts[4])       
                        nad['new_NAD'] = self.__int_or_hex(parts[5])               
                        command['NAD'] = nad                       
                    elif 'datadump' in command_lower:
                        command['SID']= 0xB4                      
                        command['type'] = 'DataDump'
                        _,_,dump_details = command_entry.strip()[:-1].partition("{")
                        parts = dump_details.split(",")             
                        command['node']= parts[0].strip()                       
                        command['dump'] = [self.__int_or_hex(d) for d in parts[1:]] # ... these should all be hex values - D1 to D5
                    elif 'saveconfiguration ' in command_lower:
                        command['SID']= 0xB6                    
                        command['type'] = 'SaveConfiguration'
                        _,_,node_name = command_entry.strip()[:-1].partition("{")
                        command['node']= node_name.strip()                       
                    elif 'assignframeidrange ' in command_lower:
                        command['SID']= 0xB7                      
                        command['type'] = 'AssignFrameIdRange'
                        _,_,frame_details = command_entry.strip()[:-1].partition("{")
                        parts = frame_details.split(",")             
                        command['node'] = parts[0].strip()
                        command['frame_index'] = self.__int_or_hex(parts[1])
                        if len(parts) > 2:
                            command['frame_PIDs'] = [self.__int_or_hex(fp) for fp in parts[2:]] # ... assuming these are all hex values (NEEDS CHECKING)
                    elif 'freeformat ' in command_lower:
                        command['type'] = 'FreeFormat'
                        _,_,data_details = command_entry.strip()[:-1].partition("{")
                        parts = data_details.split(",")                                   
                        command['free'] = [self.__int_or_hex(d) for d in parts] # ... these should all be hex values - D1 to D8
                    elif 'assignframeid ' in command_lower:
                        command['SID']= 0xB1                      
                        command['type'] = 'AssignFrameId'
                        _,_,frame_details = command_entry.strip()[:-1].partition("{")
                        parts = frame_details.split(",")             
                        command['node']= parts[0].strip()
                        command['name']= parts[1].strip()
                    else:
                        command['type'] = 'frame_name'                        
                        command['name'] = command_entry.strip()
                    if command['name'] is not None:
                        if command['name'] not in frame_delays:
                            frame_delays[command['name']] = {'unique': set(), 'all': set()}
                        frame_delays[command['name']]['unique'].add(current_delay)                     
                        frame_delays[command['name']]['all'].add((schedule_index,current_delay))                     

                    schedule_tables[table_name]['frames'].append(command)
        
        schedule_tables['__frame_delays'] = frame_delays
        return (schedule_tables,state)

		

    ##
    # @brief parses out the encoding types entries from the ldf file
    def __parseLdfSignalEncodingTypes(self):
        # As all blank lines and comment lines are stripped out, keep reading and processing
        # until we reach a block that is not part of the frames section.
        encoding_types = {}  # ... dictionary entries added in form '<frame name>': {'signal_size': None, 'initial_value': None, ???: []}
        block_depth = 1  # ... used to track if dealing with an inner-block or the outer-block entry.
        encoding_name = None
        while True:
            line = self.__getLine()
            if line is None:
                state = LdfParsingState.EOF
                break
            elif "}" == line:
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
            elif "}" == line:
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
		
		
    """ Notes: for things to do from chat with Richard ...
		createNode("nodename")
		by slave name require
		- list of signals
		- set of frames assicated with it
		- tx is slave to master
		- rx master to slave
		
		- event frames and collisions need to be looked at
		
		- list of slave object or a master object
    """


    # Exposing the dictionary for test purposes - this will be replaced by appropriate getters.		
    def getScheduleDetails(self, schedule_name=None, schedule_index=None):
        delay                  = None  # ... looks like this comes from schedule?
        checksumType           = None
        frameType              = None
        collisionScheduleIndex = None
        initialData            = None
        length                 = None
        try:
            frameId = self.ldfDictionary['Frames']['__id_to_name'][frame_name]
            frame_data = self.ldfDictionary['Frames'][frame_name]
        except:
            pass
        return (frameId,delay,checksumType,frameType,collisionScheduleIndex,initialData,length)

    # Exposing the dictionary for test purposes - this will be replaced by appropriate getters.		
    def getFrameNames(self, schedule_name=None):
        frame_list = []
        return frame_list

    # Exposing the dictionary for test purposes - this will be replaced by appropriate getters.		
    def getFrameDetails(self, frame_name=None):
        frameId                = None
        delay                  = None  
        checksumType           = None # TODO
        frameType              = None
        collisionScheduleIndex = None # TODO
        initialData            = None # TODO
        length                 = None # TODO
        try:
            frameId = self.ldfDictionary['Frames']['__id_to_name'][frame_name]
            frame_data = self.ldfDictionary['Frames'][frame_name]
            frame_type = frame_data['type']
        except:
            pass
        try:
            delay = sorted(list(self.ldfDictionary['ScheduleTables']['__frame_delays'][frame_name]))
        except:
            pass
        return (frameId,delay,checksumType,frameType,collisionScheduleIndex,initialData,length)

"""
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

"""

if __name__ == "__main__":

    ldfFile = LdfFile("../../../../McLaren_P14_SecurityLIN_3.5.ldf")
    #ldfFile = LdfFile("../../test/unitTest/Python_LIN_testLDF.ldf")

    print("\n\n")
    print("ScheduleTables:")
    schedules = ldfFile.getLdfDictionary()['ScheduleTables']
    print("Diagnostic Table:\t{0}\nDiagnostic Table Index:\t{1}\n".format(schedules['__diagnostic_table'],schedules['__diagnostic_index']))
    print("Frame Delays:\n{0}\n".format("\n".join(["  {0}: {1}".format(fd,str(schedules['__frame_delays'][fd]['unique'])) for fd in schedules['__frame_delays']])))
    print("Frame Delays:\n{0}\n".format("\n".join(["  {0}: {1}".format(fd,str(schedules['__frame_delays'][fd]['all'])) for fd in schedules['__frame_delays']])))
    del schedules['__diagnostic_table']
    del schedules['__diagnostic_index']
    del schedules['__frame_delays']
    for e in schedules:
        print("[{0}]: \nindex: {1}\nframes:\n  {2}\n".format(e,schedules[e]['index'],"\n\n  ".join(["{}".format(str(le)) for le in schedules[e]['frames']])).replace(", 'SID': None","").replace(", 'name': None","").replace(", 'NAD': None","").replace(", 'node': None","").replace(", 'dump': None","").replace(", 'free': None","").replace(", 'frame_index': None",""))
    print("\n")

	
    """
    print("\n\n")
    print("Frames:")
    frames = ldfFile.getLdfDictionary()['Frames']
    for e in frames:
        print("[{0}]: \n\t{1}\n".format(e,"\n\t".join(["{0}: {1}".format(le,str(frames[e][le])) for le in frames[e]])))
    print("\n")

    print("\n\n")
    print("DiagnosticFrames:")
    frames = ldfFile.getLdfDictionary()['DiagnosticFrames']
    for e in frames:
        print("[{0}]: \n\t{1}\n".format(e,"\n\t".join(["{0}: {1}".format(le,str(frames[e][le])) for le in frames[e]])))
    print("\n")
    """

    """
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
    """

