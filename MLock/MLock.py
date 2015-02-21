import threading

SHARE_READ = 'share_read'
SHARE_UPDATE = 'share_update'
SHARE_NO_UPDATE = 'share_no_update'
EXCLUDE_READ = 'exclude_read'
EXCLUDE = 'exclude'

def MLock(*args, **kwargs):
	return _MLock(*args, **kwargs)

class _MLock:
	def __init__(self):
		self.__shareReadCNT = 0
		self.__shareUpdateCNT = 0
		self.__shareNoUpdateCNT = 0
		self.__excludeRead = 0
		self.__exclude = 0
		self.__cond = threading.Condition(threading.Lock())		
	def acquireShareRead(self):
		rc = False
		with self.__cond:
			while self.__exclude:
				self.__cond.wait()
			else:
				self.__shareReadCNT += 1
				rc = True
		return rc		
	def releaseShareRead(self):
		with self.__cond:
			self.__shareReadCNT = max(self.__shareReadCNT - 1, 0)	
			self.__cond.notifyAll()
	def acquireShareUpdate(self):
		rc = False
		with self.__cond:
			while self.__shareNoUpdateCNT > 0 or self.__excludeRead or self.__exclude:
				self.__cond.wait()
			else:
				self.__shareUpdateCNT += 1
				rc = True
		return rc
	def releaseShareUpdate(self):
		with self.__cond:
			self.__shareUpdateCNT = max(self.__shareUpdateCNT - 1, 0)
			self.__cond.notifyAll()
	def acquireShareNoUpdate(self):
		rc = False
		with self.__cond:
			while self.__shareUpdateCNT > 0 or self.__excludeRead or self.__exclude:
				self.__cond.wait()
			else:
				self.__shareNoUpdateCNT += 1
				rc = True
		return rc
	def releaseShareNoUpdate(self):
		with self.__cond:
			self.__shareNoUpdateCNT	= max(self.__shareNoUpdateCNT - 1, 0)
			self.__cond.notifyAll()		
	def acquireExcludeRead(self):
		rc = False
		with self.__cond:
			while self.__shareUpdateCNT > 0 or self.__shareNoUpdateCNT > 0 or self.__excludeRead or self.__exclude:
				self.__cond.wait()
			else:
				self.__excludeRead = 1
				rc = True
		return rc
	def releaseExcludeRead(self):
		with self.__cond:
			self.__excludeRead = 0
			self.__cond.notifyAll()
	def acquireExclude(self):
		rc = False
		with self.__cond:
			while self.__shareReadCNT > 0 or self.__shareUpdateCNT > 0 or self.__shareNoUpdateCNT > 0 or self.__excludeRead or self.__exclude:
				self.__cond.wait()
			else:
				self.__exclude = 1
				rc = True
		return rc
	def releaseExclude(self):
		with self.__cond:
			self.__exclude = 0
			self.__cond.notifyAll()
	__acquireLock = {
		SHARE_READ : acquireShareRead,
		SHARE_UPDATE : acquireShareUpdate,
		SHARE_NO_UPDATE : acquireShareNoUpdate,
		EXCLUDE_READ : acquireExcludeRead,
		EXCLUDE : acquireExclude
	}
	__releaseLock = {
		SHARE_READ : releaseShareRead,
		SHARE_UPDATE : releaseShareUpdate,
		SHARE_NO_UPDATE : releaseShareNoUpdate,
		EXCLUDE_READ : releaseExcludeRead,
		EXCLUDE : releaseExclude
	}
	def acquire(self, type):
		_MLock.__acquireLock.get(type)(self)
	def release(self, type):
		_MLock.__releaseLock.get(type)(self)



