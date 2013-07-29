
import types
class GF:
	# GF(2^m), primitive polymonial
	def __init__(self, m, prim):
		# 13 numbers
		self.prim_poly = (0X00000000, 0X00000001, 0X00000007, 0X0000000b, 0X00000013, 0X00000025, 0X00000043, 0X00000089, 0X00000187, 0X00000211, 0X00000409, 0X00000805, 0X00001053) 
		# the field size is supported from GF(2^1) to GF(2^12).
		if m > 12 :	 
			return None
		self.gFieldSize = 1<<m
		if 0 == prim :
			prim = prim_poly[m]
			
		# init table_alpha and table_index	
		self.table_alpha = [-2] * self.gFieldSize
		self.table_index = [-2] * self.gFieldSize
		# init the first element table_alpha and table_index
		self.table_alpha[0]=1
		self.table_index[0]=-1
		# assignment table_alpha and table_index
		for i in range(1, self.gFieldSize):
			self.table_alpha[i] = self.table_alpha[i-1]<<1
			if self.table_alpha[i] >= self.gFieldSize:
				self.table_alpha[i]^=prim	
			self.table_index[self.table_alpha[i]]=i
		self.table_index[1]=0
		
		# init table_mul and table_div
		self.table_mul =  [[0 for col in range(self.gFieldSize)] for row in range(self.gFieldSize)]
		self.table_div =  [[0 for col in range(self.gFieldSize)] for row in range(self.gFieldSize)]
		for i in range(self.gFieldSize):
			for j in range(self.gFieldSize):
				self.table_mul[i][j]=self.gfmul(i,j)
				self.table_div[i][j]=self.gfdiv(i,j)
	
	# show  the contents of the array
	def gf_print(self):
		for i in range(0, self.gFieldSize):
			print "%d\t %d\t %d\n" %(i, self.table_alpha[i], self.table_index[i])

	def gf_alpha(self, n):
		return self.table_alpha[n]

	def gf_index(self, n):
		return self.table_index[n]

	def gf_neg(self, n):
		return n
		
	def gf_inv(self, n):
		return self.table_div[1][n]

	def gf_mul(self, a, b):
		return self.table_mul[a][b]

	def gf_div(self, a, b):
		return self.table_div[a][b]

	def gf_add(self, a, b):
		return a^b

	def gf_sub(self, a, b):
		return a^b

	def gf_exp(self, a, b):
		return table_alpha[self.table_index[a]*b%(self.gFieldSize-1)]
		
	def gfmul(self, a, b):
		if (0==a or 0==b):
			return 0
		return self.table_alpha[(self.table_index[a]+self.table_index[b])%(self.gFieldSize-1)]

	def gfdiv(self, a, b):
		if (0==a or 0==b):
			return 0
		return self.table_alpha[(self.table_index[a]-self.table_index[b]+(self.gFieldSize-1))%(self.gFieldSize-1)]
	
	# judge int 
	def judge_intOrchar(self, p):
		if type(p) == type(1):
			return 1
		elif type(p) == type('a'): 
			return 2
		else:
			return 0
		
	# convert char to int
	def char_2_int (self, p):
		return ord(p)	
	
	# XOR --- p1 and p2 are packet_payloads
	def gf_XOR(self, p1, p2):
		print "Enter XOR"
		len1 = len(p1)
		len2 = len(p2)
		# ternary expression in python : true_part if condition else false_part
		big = len1 if (len1 > len2) else len2
		small = len2 if (len1 > len2) else len1
		print "bigLength is: %d,   smallLength is %d " %(big, small)
		
		# put the packet contents into string buffers
		#p1->CopyData(buf1, len1)
		# here, the payload p1 and p2 are bytes Type, so we just:
		buf1 = p1
		buf2 = p2
		buffer = ['0'] * big
		
		print "start XOR low bites"
		for i in range(small):
			#buffer[i] = buffer[0:i] + unichr( ord(buf1[i])^ ord(buf2[i]) ) + buffer[i+1:] 
			#buffer[i] = unichr( ord(buf1[i])^ ord(buf2[i]) ) # unincode  16 hex
			#print chr(buffer[i]) # ascII char 
			flag1 = self.judge_intOrchar(buf1[i]) 
			flag2 = self.judge_intOrchar(buf2[i]) 
			if flag1 ==2:
				temp1 = ord(buf1[i])
			if flag2 ==2:
				temp2 = ord(buf2[i]) # ascII code  10 oct 
			buffer[i] = chr(temp1 ^ temp2)
			
		print "start XOR high bites"
		for j in range(small, big):
			if len1 > len2:
				# error: can only concatenate list (not unicode) to list
				flag3 = self.judge_intOrchar(buf1[j]) 
				if flag3 == 2:
					temp3 = ord(buf1[j])
					buffer[j] = chr(temp3^0)
			else:
				flag4 = self.judge_intOrchar(buf2[j]) 
				if flag4 == 2:
					temp4 = ord(buf2[j])
					buffer[j] = chr(temp4^0)
		print "Over XOR"
		
		# put string buffer into packet and return packet object
		#Ptr<Packet> packet = Create<Packet>(buffer, big)
		# here, buffer and paylaod are the same type BYTES,so we just
		newPacket = buffer
		return newPacket
		
	# buffer = (encodeNum1*p1)^(encodeNum2*p2)
	def encode_mul_XOR(self, p1, encodeNum1, p2, encodeNum2):
		print"Enter encode_mul_XOR"
		len1 = len(p1)
		len2 = len(p2)
		big = len1 if (len1 > len2) else len2
		small = len2 if (len1 > len2) else len1
		print "bigLength is: %d,   smallLength is %d " %(big, small)
		
		# put the packet contents into string buffers
		buf1 = p1
		buf2 = p2
		
		# start multiply for p1
		for i in range(len1):
			buf1[i] = self.gfmul(buf1[i],encodeNum1)

		# start multiply for p2
		for j in range(len2):
			buf2[j] = self.gfmul(buf2[j],encodeNum2)

		print "start XOR low bites"
		for i in range(small):
			buffer[i] = buf1[i]^buf2[i]
			
		print "start XOR high bites"
		for j in range(small, big):
			if len1 > len2:
				buffer[j] = buf1[j]^0
			else:
				buffer[j] = buf2[j]^0
		print "Over XOR"
		
		# put string buffer into packet and return packet object
		newPacket = buffer
		return newPacket

		
	# buffer = ((originPkt*encodeNum1)^(codedPkt))/encodeNum2
	def decode_div_XOR( originPkt, encodeNum1, encodeNum2, codedPkt):
		print "Enter decode_div_XOR"
		len1 = len(p1)
		len2 = len(p2)
		big = len1 if (len1 > len2) else len2
		small = len2 if (len1 > len2) else len1
		print "bigLength is: %d,   smallLength is %d " %(big, small)
		
		# put the packet contents into string buffers
		buf1 = p1
		buf2 = p2
		
		# start mutiply for originPkt
		for i in range(len1):
			buf1[i] = self.gfmul(buf1[i],encodeNum1)
		

		print "start XOR low bites"
		for i in range(small):
			buffer[i] = buf1[i] ^ buf2[i]

		print "start XOR high bites"
		for j in range(small, big):
			if len1 > len2:
				buffer[j]  = buf1[j] ^0
			else:
				buffer[j] = buf2[j] ^0
		print "Over XOR"
		
		# start divide for buffer to get originalPkt2
		for k in range(len1):
			buffer[i] = self.gfdiv(buffer[i],encodeNum2)
		
		# put string buffer into packet and return packet object
		newPacket = buffer
		return newPacket

if __name__ == "__main__" :
	# init the GF(2^8)
	gf = GF(8, 0X187)
	'''
	#gf.gf_print()
	print " 98 + 97 = %d" %(gf.gf_add(97,98))
	print " 129 * 5 = %d" %(gf.gf_mul(129,5))
	print " 12 / 129 = %d" %(gf.gf_div(12,129))
	# gf_mul(a,b) lookup the outcome from mulTable; while gfmul(a,b) caculate the outcome----outcome is the same
	print " 129 * 5 = %d" %(gf.gfmul(129,5))
	'''
	
	'''
	p1 = 'a'
	p2 = 'b'
	print "'a' ^ 'b' = %d" %(ord(p1) ^ ord(p2))
	print "'a' ^ 'b' = %s" % chr(ord(p1) ^ ord(p2))
	'''
	
	'''
	#test for number_string
	s1 = '11111'
	s2 = '22222'
	sMUL = '99999'
	for i in range(len(s1)):
		print s1[i], s2[i], sMUL[i+1:]
		sMUL = sMUL[0:i] + str(gf.gf_add(int(s1[i]), int(s2[i]))) + sMUL[i+1:]
	print sMUL
	'''
	'''
	#test for ASCII code string
	s1 = 'aaaaa'
	s2 = 'bbbbb'
	sMUL = 'ccccc'
	for i in range(len(s1)):
		print s1[i], s2[i],sMUL[i+1:]
		sMUL = sMUL[0:i] + unichr(gf.gf_add(ord(s1[i]), ord(s2[i]))) + sMUL[i+1:]
	print sMUL
	'''
	
	'''
	# test for packets
	p1 = 'sssssss'
	p2 = 'ddddddddddd'
	newP = gf.encode_mul_XOR(p1, 1, p2, 1)
	originP1 = gf.decode_div_XOR(p2, 1, 1, newP)
	print newP
	print originP1
	'''
	
	
	# test for packets
	p1 = 'sssssss'
	p2 = 'ddddddddddd'
	newP = gf.gf_XOR(p1,p2)
	
	originP1 = (gf.gf_XOR(newP, p2))[1:len(p1)]
	print newP
	print originP1
	