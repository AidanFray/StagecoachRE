# Stagecoach RE
We're aiming to obtain the colour and the `Word-of-the-day` for the Stagecoach app.

This is word that is shown each day on the ticket screen. This is used to allow the driver to quickly check for the apps validity.

![](images/ticket.png)

## Recon
Opening up the application in `jadx` gives us some interesting starting points.

The most fruitful was the `WordOfTheDayFile`.

The file looks something like the snippet below. Elements have been removed for brevity:

```java
package com.stagecoachbus.logic;

import android.support.graphics.drawable.PathInterpolatorCompat;
import java.io.ByteArrayOutputStream;
import java.io.IOException;

public class WordOfTheDayFile {

    /* renamed from: a */
    private final byte[] f5539a;

    public WordOfTheDayFile() {
        byte[] bArr = new byte[PathInterpolatorCompat.MAX_NUM_POINTS];
        // fill-array-data instruction
        bArr[0] = 42;
        bArr[1] = -40;
        bArr[2] = 107;
        bArr[3] = 60;
        bArr[4] = -124;
        bArr[5] = 99;
        bArr[6] = -17;
        bArr[7] = 62;
        bArr[8] = 74;
        bArr[9] = 89;
        bArr[10] = -55;
        bArr[11] = 5;
        [...]
        bArr[2986] = -31;
        bArr[2987] = -96;
        bArr[2988] = 104;
        bArr[2989] = -69;
        bArr[2990] = 114;
        bArr[2991] = 71;
        bArr[2992] = -63;
        bArr[2993] = -59;
        bArr[2994] = 56;
        bArr[2995] = -95;
        bArr[2996] = -42;
        bArr[2997] = -72;
        bArr[2998] = -113;
        bArr[2999] = 42;
        this.f5546a = bArr;
    }

    public byte[] getBytesArray() throws IOException {
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream(27000);
        byteArrayOutputStream.write(this.f5539a);
        byteArrayOutputStream.write(new WordOfTheDayFile0().f5540a);
        byteArrayOutputStream.write(new WordOfTheDayFile1().f5541a);
        byteArrayOutputStream.write(new WordOfTheDayFile2().f5542a);
        byteArrayOutputStream.write(new WordOfTheDayFile3().f5543a);
        byteArrayOutputStream.write(new WordOfTheDayFile4().f5544a);
        byteArrayOutputStream.write(new WordOfTheDayFile5().f5545a);
        byteArrayOutputStream.write(new WordOfTheDayFile6().f5546a);
        byteArrayOutputStream.write(new WordOfTheDayFile7().f5547a);
        return byteArrayOutputStream.toByteArray();
    }
}
```

Exporting the byte values from `getBytesArray()` gives us something that looks encrypted.

Looking at the usages for this class directs us towards some logic that looks like it is decrypting the values with `AES256` and saving it within a database. The code snippet is below:

```java
/* renamed from: g */
public void mo17651g(Realm realm) throws IOException, BadPaddingException {
    AES256Cipher_ a = AES256Cipher_.m8997a(this.f5278a);
    byte[] bytesArray = new WordOfTheDayFile().getBytesArray();
    HidingUtils hidingUtils = new HidingUtils();
    realm.executeTransaction(new DatabaseManager$$Lambda$2(this, a.mo20151a(bytesArray, hidingUtils.unhide(this.f5278a.getString(R.string.wotday_k) + "diWfZOZwsWsI0ThXoFb8+Y=").getBytes())));
}
```

What stands out at the stage is this `HidingUtils()` being created. If we look at the class definition it shows us that it is loading a custom JNI lib called `ticket-ref-code`:

```java
package com.lagoru.jnirealm;

public class HidingUtils {
    public native String unhide(String str);

    static {
        System.loadLibrary("ticket-ref-code");
    }
}
```

Lets take this lib into ghidra and take a look.

Mapping this `native` library call to the method in the binary was trivial. The application authors had not stripped the JNI formatted name: ` Java_com_lagoru_jnirealm_HidingUtils_unhide`.


## Unhide

Unhide contains a few calls to `Base64Decode` and a hardcoded base64 string (`"ZKxPX5pg1nhOsMRY3LtSC56mP6Df8YeYE3yjGLJssNY="`)

With some further investigation it looks like the code is decoding the base64 input and the hardcoded string as bytes and then looping around each byte and XORing.

If we look back at the original input we can see the input: `(R.string.wotday_k) + "diWfZOZwsWsI0ThXoFb8+Y="`

Looking for `R.string.wotday_k` gives us over all the base64 string:

```
V5R5b9kl4DoLh/Mcmo9jSdiWfZOZwsWsI0ThXoFb8+Y=
```

Thus, xoring the string base64 strings gives us the ascii: `3860CE6BE77DF41BF0B3F3B408BF37C0`!

This looks like the key that is being passed into the `AES256` instance.

## Decryption

The final step is to find more information around the suspected AES decryption. The method being called with the result from `unhide` is shown below:

```java
public String mo20151a(byte[] bArr, byte[] bArr2) throws BadPaddingException {
    if (bArr == null) {
        return null;
    }
    try {
        byte[] b = mo20159b(f6260c, bArr2, bArr);
        if (b != null) {
            return new String(b, "UTF-8");
        }
        return null;
    } catch (UnsupportedEncodingException e) {
        ThrowableExtension.m3077a(e);
        return null;
    } catch (NoSuchAlgorithmException e2) {
        ThrowableExtension.m3077a(e2);
        return null;
    } catch (NoSuchPaddingException e3) {
        ThrowableExtension.m3077a(e3);
        return null;
    } catch (InvalidKeyException e4) {
        ThrowableExtension.m3077a(e4);
        return null;
    } catch (InvalidAlgorithmParameterException e5) {
        ThrowableExtension.m3077a(e5);
        return null;
    } catch (IllegalBlockSizeException e6) {
        ThrowableExtension.m3077a(e6);
        return null;
    }
}

public byte[] mo20159b(byte[] bArr, byte[] bArr2, byte[] bArr3) throws UnsupportedEncodingException, NoSuchAlgorithmException, NoSuchPaddingException, InvalidKeyException, InvalidAlgorithmParameterException, IllegalBlockSizeException, BadPaddingException {
    IvParameterSpec ivParameterSpec = new IvParameterSpec(bArr);
    SecretKeySpec secretKeySpec = new SecretKeySpec(bArr2, "AES/CBC/PKCS5PADDING");
    Cipher instance = Cipher.getInstance("AES/CBC/PKCS5PADDING");
    instance.init(2, secretKeySpec, ivParameterSpec);
    return instance.doFinal(bArr3);
}
```

We can gathering from this is that the `AES` decryption is using `CBC` and is passing this object `f6260c` as well as the `key` and wordfile bytes. This is out IV!

This is contained as a static variable in the file:

```java
private static byte[] f6260c = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
```

This gives us what we need to decrypt the word files.

## PoC

Below is the `python` code used to successfully decrypt the word files:

```python
from Crypto.Cipher import AES

key = b"3860CE6BE77DF41BF0B3F3B408BF37C0"
iv  = bytes.fromhex("00000000000000000000000000000000")

with open("WordFile", 'rb') as file:
    data = file.read()

cipher = AES.new(key, AES.MODE_CBC, iv)

d = cipher.decrypt(data)

print(d.decode())
```

Initially I thought the key was to be decoded as hex into a 16-byte value, but as the application is using AES256 and this needs a 32 byte value, the key string needs to be converted directly from ascii to bytes.

Running this produces a json file with the word and colours:

```json
[
 {
   "day": 1,
   "word": "Tuner",
   "colour": "Orange"
 },
 {
   "day": 2,
   "word": "Bongo",
   "colour": "Orange"
 },
 {
   "day": 3,
   "word": "Solve",
   "colour": "Green"
 },
 [...]
 {
   "day": 364,
   "word": "Train",
   "colour": "Pink"
 },
 {
   "day": 365,
   "word": "Bingo",
   "colour": "Orange"
 },
 {
   "day": 366,
   "word": "Beech",
   "colour": "Grey"
 }
]
```