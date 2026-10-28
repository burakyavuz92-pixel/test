using System.Text.Json;

public record ViewCamera(double[] Direction,double[] Up,string Projection,string Confidence);
public static class OcctSheetService
{
    public static ViewCamera Camera(JsonElement root,bool allowApproximate=false)
    {
        var camera=root.GetProperty("camera").Deserialize<ViewCamera>(new JsonSerializerOptions{PropertyNameCaseInsensitive=true})??throw new Exception("Kamera tarifi yok.");
        ValidateCamera(camera,allowApproximate);return camera;
    }
    public static void ValidateCamera(ViewCamera c,bool allowApproximate=false)
    {
        if(c.Direction?.Length!=3||c.Up?.Length!=3||c.Direction.Any(v=>!double.IsFinite(v))||c.Up.Any(v=>!double.IsFinite(v)))throw new Exception("Geçersiz kamera vektörü.");
        double Len(double[] x)=>Math.Sqrt(x.Sum(v=>v*v));
        double dn=Len(c.Direction),un=Len(c.Up);
        if(dn<1e-6||un<1e-6||Math.Abs(c.Direction.Zip(c.Up).Sum(v=>v.First*v.Second))/(dn*un)>.98)throw new Exception("Kamera yönü ve yukarı vektörü çakışıyor.");
        if(c.Direction[2]<=0||c.Projection!="orthographic"||(c.Confidence is not ("high" or "medium") && !(allowApproximate && c.Confidence=="low")))throw new Exception("Kamera desteklenmiyor/belirsiz; kapalı ön yüz +Z tarafındadır.");
    }
}
