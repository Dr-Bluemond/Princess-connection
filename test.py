import uiautomator2 as u2
from cv import *

d = u2.connect()
dWidth, dHeight = d.window_size()
print(dWidth, dHeight)
screenshot = d.screenshot(format="opencv")
cv2.imwrite('test.jpg', screenshot)
img = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
img = UIMatcher.Rotate(img)
plt.imshow(img)
plt.show()
