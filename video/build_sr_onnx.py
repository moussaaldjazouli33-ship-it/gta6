"""
Converts the open-source UpscalerJS ESRGAN-slim (RDN, DIV2K) x2 TF.js layers model
(npm @upscalerjs/esrgan-slim, MIT) into ONNX so it runs with onnxruntime on CPU.

    python video/build_sr_onnx.py <path-to>/esrgan-slim/models/x2/model.json video/models/esrgan_slim_x2.onnx
"""
import json
import os
import sys

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper


def main(model_json, out):
    m = json.load(open(model_json))
    layers = m["modelTopology"]["model_config"]["config"]["layers"]
    # weights
    blob = b"".join(open(os.path.join(os.path.dirname(model_json), p), "rb").read()
                    for g in m["weightsManifest"] for p in g["paths"])
    weights, off = {}, 0
    for g in m["weightsManifest"]:
        for w in g["weights"]:
            n = int(np.prod(w["shape"]))
            weights[w["name"]] = np.frombuffer(blob, np.float32, n, off).reshape(w["shape"])
            off += n * 4
    nodes, inits = [], []
    name_out = {}
    for L in layers:
        c, cfg = L["class_name"], L["config"]
        name = cfg["name"]
        ins = [name_out[i[0]] for i in L["inbound_nodes"][0]] if L["inbound_nodes"] else []
        o = name
        if c == "InputLayer":
            name_out[name] = "input"
            continue
        if c == "Conv2D":
            k = weights[f"{name}/kernel"].transpose(3, 2, 0, 1).copy()
            b = weights[f"{name}/bias"]
            inits += [numpy_helper.from_array(k, f"{name}_W"), numpy_helper.from_array(b, f"{name}_B")]
            kh, kw = cfg["kernel_size"]
            pads = [kh // 2, kw // 2, kh // 2, kw // 2] if cfg["padding"] == "same" else [0, 0, 0, 0]
            nodes.append(helper.make_node("Conv", [ins[0], f"{name}_W", f"{name}_B"], [o], pads=pads,
                                          kernel_shape=[kh, kw]))
            assert cfg.get("activation", "linear") == "linear"
        elif c == "Activation":
            assert cfg["activation"] == "relu"
            nodes.append(helper.make_node("Relu", ins, [o]))
        elif c == "Concatenate":
            nodes.append(helper.make_node("Concat", ins, [o], axis=1))
        elif c == "Add":
            nodes.append(helper.make_node("Sum", ins, [o]))
        elif c == "UpSampling2D":
            sh, sw = cfg["size"]
            sc = numpy_helper.from_array(np.array([1, 1, sh, sw], np.float32), f"{name}_scales")
            inits.append(sc)
            mode = "nearest" if cfg.get("interpolation", "nearest") == "nearest" else "linear"
            nodes.append(helper.make_node("Resize", [ins[0], "", f"{name}_scales"], [o], mode=mode))
        else:
            raise ValueError(c)
        name_out[name] = o
    last = name_out[layers[-1]["config"]["name"]]
    graph = helper.make_graph(nodes, "esrgan_slim_x2",
                              [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, 3, None, None])],
                              [helper.make_tensor_value_info(last, TensorProto.FLOAT, [1, 3, None, None])], inits)
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
    model.ir_version = 8
    onnx.checker.check_model(model)
    onnx.save(model, out)
    print("wrote", out, f"({len(nodes)} nodes)")


if __name__ == "__main__":
    main(*sys.argv[1:3])
