using System.Text.Json;

// Coordinates are declared by the vision model, not entered by the user.
public static class CadReferenceFrame
{
    public static void Validate(JsonElement source)
    {
        var frame=source.GetProperty("coordinateFrame");var view=frame.GetProperty("referenceView");
        if(string.IsNullOrWhiteSpace(view.GetProperty("id").GetString()))throw new Exception("Referans görünüş kimliği eksik.");
        var box=view.GetProperty("bbox01").EnumerateArray().Select(v=>v.GetDouble()).ToArray();
        var point=frame.GetProperty("origin").GetProperty("point01").EnumerateArray().Select(v=>v.GetDouble()).ToArray();
        if(box.Length!=4||box.Any(v=>!double.IsFinite(v)||v<0||v>1)||box[0]>=box[2]||box[1]>=box[3])throw new Exception("Referans görünüş alanı geçersiz.");
        if(point.Length!=2||point.Any(v=>!double.IsFinite(v))||point[0]<box[0]||point[0]>box[2]||point[1]<box[1]||point[1]>box[3])throw new Exception("Orijin işareti referans görünüşün dışında.");
        var origin=frame.GetProperty("origin");
        if(origin.GetProperty("kind").GetString() is not ("axis-face-intersection" or "datum"))throw new Exception("Orijin referans türü desteklenmiyor.");
        if(string.IsNullOrWhiteSpace(origin.GetProperty("evidence").GetString()))throw new Exception("Orijinin geometrik kanıtı eksik.");
        var axes=frame.GetProperty("axes");
        // Sheet projection currently uses this right-handed basis. Never silently reflect another basis.
        if(axes.GetProperty("x").GetString()!="right"||axes.GetProperty("y").GetString()!="up"||axes.GetProperty("z").GetString()!="toward-viewer")throw new NotSupportedException("Bu eksen bazı yerel görünüş adaptöründe desteklenmiyor.");
        var anchor=frame.GetProperty("bodyAnchor");
        if(origin.GetProperty("kind").GetString()=="axis-face-intersection"&&origin.GetProperty("feature").GetString()=="body"&&
           (anchor.GetProperty("x").GetProperty("kind").GetString()!="origin"||anchor.GetProperty("y").GetProperty("kind").GetString()!="origin"))throw new Exception("Gövde eksenindeki orijin ile gövde ankrajı çelişiyor.");
    }
}
