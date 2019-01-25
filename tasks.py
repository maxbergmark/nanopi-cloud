import rsa

def newkeys(bits):
	pub, pri = rsa.newkeys(bits)
	return pub, pri