import Foundation
import Vision
import ImageIO
let folder=URL(fileURLWithPath:CommandLine.arguments[1]);let files=try FileManager.default.contentsOfDirectory(at:folder,includingPropertiesForKeys:nil).filter{$0.pathExtension=="png"}.sorted{$0.path<$1.path}
var result:[String:[String]]=[:]
for file in files {autoreleasepool {do {let request=VNRecognizeTextRequest();request.recognitionLevel = .accurate;request.usesLanguageCorrection=false;request.recognitionLanguages=["en-US"];request.usesCPUOnly=true;try VNImageRequestHandler(url:file,options:[:]).perform([request]);result[file.lastPathComponent]=(request.results ?? []).compactMap{$0.topCandidates(1).first?.string}}catch{result[file.lastPathComponent]=["ERROR: \(error)"]}}}
let output=try JSONSerialization.data(withJSONObject:result,options:[.prettyPrinted,.sortedKeys]);FileHandle.standardOutput.write(output)
