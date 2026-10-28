public static class ImageDensity
{
    public static int ReadJpegDpi(string path)
    {
        var b=File.ReadAllBytes(path);if(b.Length<4||b[0]!=255||b[1]!=216)throw new Exception("DPI okuma yalnızca JPEG/JFIF için destekleniyor.");
        int i=2;
        while(i+4<=b.Length && b[i]==255)
        {
            byte marker=b[i+1];if(marker==218||marker==217)break;
            int length=b[i+2]*256+b[i+3];if(length<2||i+2+length>b.Length)break;
            if(marker==224 && length>=16 && b[i+4]==74 && b[i+5]==70 && b[i+6]==73 && b[i+7]==70)
            {
                int unit=b[i+11],x=b[i+12]*256+b[i+13],y=b[i+14]*256+b[i+15];
                if(unit==2){x=(int)Math.Round(x*2.54);y=(int)Math.Round(y*2.54);}
                if(unit is 1 or 2 && x>0 && x==y)return x;
            }
            i+=length+2;
        }
        throw new Exception("Kaynakta desteklenen eşit X/Y JFIF DPI değeri yok; varsayılan DPI atanmadı.");
    }
}
