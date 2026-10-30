using System.Globalization;
using System.Text.Json;
using System.Text.Json.Nodes;

// Public v8 has self-contained values. Lowering and arithmetic belong to software, not the model.
public static class CadRecipeV8
{
    public static bool IsV8(JsonElement recipe)=>recipe.TryGetProperty("schemaVersion",out var v)&&v.GetInt32()==8;
    public static double Evaluate(string expression, IReadOnlyDictionary<string,double?> columns)
        =>new Arithmetic(expression,columns).Run();
    sealed class Arithmetic(string text,IReadOnlyDictionary<string,double?> columns)
    {
        int pos,depth;
        void Space(){while(pos<text.Length&&char.IsWhiteSpace(text[pos]))pos++;}
        bool Eat(char c){Space();if(pos<text.Length&&text[pos]==c){pos++;return true;}return false;}
        double Sum(){double x=Product();while(true){if(Eat('+'))x+=Product();else if(Eat('-'))x-=Product();else return x;}}
        double Product(){double x=Atom();while(true){if(Eat('*'))x*=Atom();else if(Eat('/')){double y=Atom();if(y==0)throw new Exception("Sıfıra bölme.");x/=y;}else return x;}}
        double Atom()
        {
            if(++depth>64)throw new Exception("İfade çok derin.");
            try{
                if(Eat('+'))return Atom();if(Eat('-'))return -Atom();
                if(Eat('(')){double x=Sum();if(!Eat(')'))throw new Exception("İfade parantezi kapanmadı.");return x;}
                Space();int start=pos;
                if(pos<text.Length&&(char.IsLetter(text[pos])||text[pos]=='_'))
                {
                    while(pos<text.Length&&(char.IsLetterOrDigit(text[pos])||text[pos]=='_'))pos++;
                    string id=text[start..pos];
                    if(!columns.TryGetValue(id,out var v)||v is null)throw new Exception("İfade boş/bilinmeyen sütun kullanıyor: "+id);
                    return v.Value;
                }
                while(pos<text.Length&&(char.IsDigit(text[pos])||text[pos]=='.'))pos++;
                if(start==pos)throw new Exception("Geçersiz aritmetik ifade.");
                return double.Parse(text[start..pos],CultureInfo.InvariantCulture);
            }finally{depth--;}
        }
        public double Run(){if(text.Length>2048)throw new Exception("İfade çok uzun.");double x=Sum();Space();if(pos!=text.Length||!double.IsFinite(x))throw new Exception("Geçersiz/sonlu olmayan aritmetik ifade.");return x;}
    }
    public static JsonElement Lower(JsonElement recipe,Dictionary<string,string> row)
    {
        var root=JsonNode.Parse(recipe.GetRawText())!;
        var cells=ExcelModelInput.Build(new[]{row}).rows[0].cells;
        var values=cells.ToDictionary(kv=>kv.Key,kv=>kv.Value.nominalMm);
        var parameters=new JsonArray();
        foreach(var cell in cells)parameters.Add(new JsonObject{["id"]="col_"+cell.Key,["unit"]="mm",["source"]=new JsonObject{["kind"]="column",["column"]=cell.Key}});
        JsonNode? Bind(JsonNode? n)
        {
            if(n is JsonObject obj){
                if(obj.Count==1&&obj["expr"] is JsonValue expression)return JsonValue.Create(Evaluate(expression.GetValue<string>(),values));
                if(obj.Count==1&&obj["column"] is JsonValue col)return new JsonObject{["param"]="col_"+col.GetValue<string>()};
                var copy=new JsonObject();foreach(var kv in obj)copy[kv.Key]=Bind(kv.Value);return copy;
            }
            if(n is JsonArray a){var copy=new JsonArray();foreach(var item in a)copy.Add(Bind(item));return copy;}
            return n?.DeepClone();
        }
        var geometry=root["geometry"]!;
        var frames=geometry["frames"]?.DeepClone().AsArray()??new JsonArray();
        if(frames.Any(f=>f!["id"]!.GetValue<string>()=="world"))throw new Exception("world bazı yazılım tarafından sağlanır.");
        frames.Insert(0,JsonNode.Parse("""{"id":"world","origin":[0,0,0],"xAxis":[1,0,0],"zAxis":[0,0,1]}"""));
        geometry["frames"]=Bind(frames);geometry["parameters"]=parameters;
        foreach(var f in geometry["features"]!.AsArray())
        {
            string kind=f!["kind"]!.GetValue<string>();var uses=new JsonArray();
            void Add(string key){if(f[key] is JsonValue val)uses.Add(val.GetValue<string>());else throw new Exception("İşlem alanı eksik: "+key);}
            if(kind is "hole" or "fillet" or "chamfer" or "cut" or "fuse")Add("body");
            if(kind=="cut")Add("tool");
            if(kind=="fuse")foreach(var item in f["additions"]!.AsArray())uses.Add(item!.GetValue<string>());
            if(kind is "extrude" or "revolve")Add("sketch");
            if(kind is "circularPattern" or "linearPattern")Add("seed");
            f["uses"]=uses;f["frame"]??=JsonValue.Create("world");
            bool active=true;
            if(f["presence"]?["kind"]?.GetValue<string>()=="columnPresent")active=cells[f["presence"]!["column"]!.GetValue<string>()].state!="blank";
            // Inactive optional geometry must not evaluate expressions containing blank cells.
            if(active)f["args"]=Bind(f["args"]);
            else {
                JsonNode? Neutral(JsonNode? n){if(n is JsonObject o){if(o.Count==1&&o["expr"] is not null)return JsonValue.Create(0);var c=new JsonObject();foreach(var kv in o)c[kv.Key]=Neutral(kv.Value);return c;}if(n is JsonArray a){var c=new JsonArray();foreach(var x in a)c.Add(Neutral(x));return c;}return n?.DeepClone();}
                f["args"]=Neutral(f["args"]);
            }
            foreach(var key in new[]{"body","tool","additions","sketch","seed"})f.AsObject().Remove(key);
        }
        var drawing=root["drawing"]!;
        foreach(var dim in drawing["dimensions"]!.AsArray())
        {
            var source=dim!["valueSource"]!;
            if(source["kind"]!.GetValue<string>()=="constant"){
                string id="fixed_dimension_"+parameters.Count;
                parameters.Add(new JsonObject{["id"]=id,["unit"]=source["unit"]?.DeepClone()??JsonValue.Create("mm"),["source"]=new JsonObject{["kind"]="constant",["value"]=source["value"]!.DeepClone()}});
                dim["valueSource"]=new JsonObject{["kind"]="parameter",["parameter"]=id};
            }
        }
        drawing["sections"]=Bind(drawing["sections"]);
        drawing["geometricTolerances"]=Bind(drawing["geometricTolerances"]);
        root["schemaVersion"]=7;
        return JsonSerializer.SerializeToElement(root);
    }
    public static List<WorkflowIssue> Check(JsonElement recipe,List<Dictionary<string,string>> rows)
    {
        var issues=new List<WorkflowIssue>();
        foreach(var row in rows)try{issues.AddRange(CadRecipeV7.Check(Lower(recipe,row),new(){row}));}
        catch(Exception ex){issues.Add(new("RECIPE_V8_CONTRACT","model","error",row["jpeg file name"]+": "+ex.Message,[],""));}
        return issues;
    }
}
