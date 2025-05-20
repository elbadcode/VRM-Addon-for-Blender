# SPDX-License-Identifier: MIT OR GPL-3.0-or-later
import dataclasses
import datetime
import logging
from collections.abc import Set as AbstractSet
from typing import Optional

import bpy
from bpy.types import Context, Event, Image, Material, Operator
from io_scene_gltf2.io.com import gltf2_io

from ..common.logger import get_logger

logger = get_logger(__name__)


class WM_OT_vrm_io_scene_gltf2_disabled_warning(Operator):
    bl_label = "glTF 2.0 add-on is disabled"
    bl_idname = "wm.vrm_gltf2_addon_disabled_warning"
    bl_options: AbstractSet[str] = {"REGISTER"}

    def execute(self, _context: Context) -> set[str]:
        return {"FINISHED"}

    def invoke(self, context: Context, _event: Event) -> set[str]:
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, _context: Context) -> None:
        self.layout.label(
            text='Official add-on "glTF 2.0 format" is required. Please enable it.'
        )


def image_to_image_bytes(
    image: Image, export_settings: dict[str, object]
) -> tuple[bytes, str]:
    mime_type = "image/jpeg" if image.file_format == "JPEG" else "image/png"

    if bpy.app.version < (3, 6, 0):
        from io_scene_gltf2.blender.exp.gltf2_blender_image import (
            ExportImage as ExportImage_Before_3_6,
        )

        export_image_before_3_6 = ExportImage_Before_3_6.from_blender_image(image)

        if bpy.app.version < (3, 5, 0):
            encoded = export_image_before_3_6.encode(mime_type)
            if isinstance(encoded, bytes):
                # bpy.app.version < (3, 3, 0)
                return encoded, mime_type
            image_bytes, _specular_color_factor = encoded
            return image_bytes, mime_type

        image_bytes, _specular_color_factor = export_image_before_3_6.encode(
            mime_type, export_settings
        )
        return image_bytes, mime_type

    if bpy.app.version < (4, 3):
        from io_scene_gltf2.blender.exp.material.extensions.gltf2_blender_image import (
            ExportImage as ExportImage_Before_4_3,
        )

        export_image_before_4_3 = ExportImage_Before_4_3.from_blender_image(image)
        image_bytes, _specular_color_factor = export_image_before_4_3.encode(
            mime_type, export_settings
        )
        return image_bytes, mime_type

    from io_scene_gltf2.blender.exp.material.encode_image import ExportImage

    export_image = ExportImage.from_blender_image(image)
    image_bytes, _specular_color_factor = export_image.encode(
        mime_type, export_settings
    )
    return image_bytes, mime_type


def init_extras_export() -> None:
    try:
        if bpy.app.version < (4, 5, 0):
            from io_scene_gltf2.blender.com.gltf2_blender_extras import BLACK_LIST
        else:
            from io_scene_gltf2.blender.com.extras import BLACK_LIST
    except ImportError:
        return
    key = "vrm_addon_extension"
    if key not in BLACK_LIST:
        BLACK_LIST.append(key)


def create_export_settings() -> dict[str, object]:
    # https://github.com/KhronosGroup/glTF-Blender-IO/blob/b9bdc358ebf41e5f14be397d0d612cc8d645a09e/addons/io_scene_gltf2/__init__.py#L1054
    loglevel = logging.INFO

    export_settings: dict[str, object] = {
        "loglevel": loglevel,
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/67b2ed150b0eba08129b970dbe1116c633a77d24/addons/io_scene_gltf2/__init__.py#L522
        "timestamp": datetime.datetime.now(datetime.timezone.utc),
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/67b2ed150b0eba08129b970dbe1116c633a77d24/addons/io_scene_gltf2/__init__.py#L258-L268
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/67b2ed150b0eba08129b970dbe1116c633a77d24/addons/io_scene_gltf2/__init__.py#L552
        "gltf_materials": True,
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/67b2ed150b0eba08129b970dbe1116c633a77d24/addons/io_scene_gltf2/__init__.py#L120-L137
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/67b2ed150b0eba08129b970dbe1116c633a77d24/addons/io_scene_gltf2/__init__.py#L532
        "gltf_format": "GLB",
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/67b2ed150b0eba08129b970dbe1116c633a77d24/addons/io_scene_gltf2/__init__.py#L154-L168
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/67b2ed150b0eba08129b970dbe1116c633a77d24/addons/io_scene_gltf2/__init__.py#L533
        "gltf_image_format": "AUTO",
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/67b2ed150b0eba08129b970dbe1116c633a77d24/addons/io_scene_gltf2/__init__.py#L329-L333
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/67b2ed150b0eba08129b970dbe1116c633a77d24/addons/io_scene_gltf2/__init__.py#L569
        "gltf_extras": True,
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/67b2ed150b0eba08129b970dbe1116c633a77d24/addons/io_scene_gltf2/__init__.py#L611-L633
        "gltf_user_extensions": [],
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/67b2ed150b0eba08129b970dbe1116c633a77d24/addons/io_scene_gltf2/__init__.py#L606
        "gltf_binary": bytearray(),
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/67b2ed150b0eba08129b970dbe1116c633a77d24/addons/io_scene_gltf2/__init__.py#L176-L184
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/67b2ed150b0eba08129b970dbe1116c633a77d24/addons/io_scene_gltf2/__init__.py#L530
        "gltf_keep_original_textures": False,
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/bfe4ff8b1b5c26ba17b0531b67798376147d9fa7/addons/io_scene_gltf2/__init__.py#L273-L279
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/bfe4ff8b1b5c26ba17b0531b67798376147d9fa7/addons/io_scene_gltf2/__init__.py#L579
        "gltf_original_specular": False,
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/e662c281fc830d7ad3ea918d38c6a1881ee143c5/addons/io_scene_gltf2/__init__.py#L208-L214
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/e662c281fc830d7ad3ea918d38c6a1881ee143c5/addons/io_scene_gltf2/__init__.py#L617
        "gltf_jpeg_quality": 75,
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/a2eac6c4b4ef957b654b61970dc554e3803a642e/addons/io_scene_gltf2/__init__.py#L233-L240
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/a2eac6c4b4ef957b654b61970dc554e3803a642e/addons/io_scene_gltf2/__init__.py#L787
        "gltf_image_quality": 75,
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/765c1bd8f59ce34d6e346147f379af191969777f/addons/io_scene_gltf2/__init__.py#L785
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/765c1bd8f59ce34d6e346147f379af191969777f/addons/io_scene_gltf2/__init__.py#L201-L208
        "gltf_add_webp": False,
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/2debd75ace303f3a3b00a43e9d7a9507af32f194/addons/io_scene_gltf2/__init__.py#L941
        "exported_images": {},
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/2debd75ace303f3a3b00a43e9d7a9507af32f194/addons/io_scene_gltf2/__init__.py#L942
        "exported_texture_nodes": [],
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/2debd75ace303f3a3b00a43e9d7a9507af32f194/addons/io_scene_gltf2/__init__.py#L943
        "additional_texture_export": [],
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/2debd75ace303f3a3b00a43e9d7a9507af32f194/addons/io_scene_gltf2/__init__.py#L944
        "additional_texture_export_current_idx": 0,
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/2debd75ace303f3a3b00a43e9d7a9507af32f194/addons/io_scene_gltf2/__init__.py#L985-L986
        "gltf_unused_textures": False,
        "gltf_unused_images": False,
        # for https://github.com/KhronosGroup/glTF-Blender-IO/blob/06f0f908e883add2767fde828f52a013086a17c3/addons/io_scene_gltf2/blender/exp/material/extensions/gltf2_blender_gather_materials_emission.py#L72
        "current_paths": {},
        # for https://github.com/KhronosGroup/glTF-Blender-IO/blob/06f0f908e883add2767fde828f52a013086a17c3/addons/io_scene_gltf2/blender/exp/material/gltf2_blender_gather_materials.py#L171
        # https://github.com/KhronosGroup/glTF-Blender-IO/blob/06f0f908e883add2767fde828f52a013086a17c3/addons/io_scene_gltf2/blender/exp/gltf2_blender_gather.py#L62-L66
        "KHR_animation_pointer": {"materials": {}, "lights": {}, "cameras": {}},
    }

    if bpy.app.version < (4, 2):
        return export_settings

    if bpy.app.version < (4, 3):
        from io_scene_gltf2.io.com.gltf2_io_debug import Log as Log_Before_4_3

        export_settings["log"] = Log_Before_4_3(loglevel)
    else:
        from io_scene_gltf2.io.com.debug import Log

        export_settings["log"] = Log(loglevel)

    return export_settings


@dataclasses.dataclass
class ImportSceneGltfArguments:
    filepath: str
    import_pack_images: bool
    bone_heuristic: str
    guess_original_bind_pose: bool
    disable_bone_shape: bool


def import_scene_gltf(arguments: ImportSceneGltfArguments) -> set[str]:
    if bpy.app.version < (4, 2):
        return bpy.ops.import_scene.gltf(
            filepath=arguments.filepath,
            import_pack_images=arguments.import_pack_images,
            bone_heuristic=arguments.bone_heuristic,
            guess_original_bind_pose=arguments.guess_original_bind_pose,
        )

    return bpy.ops.import_scene.gltf(
        filepath=arguments.filepath,
        import_pack_images=arguments.import_pack_images,
        bone_heuristic=arguments.bone_heuristic,
        guess_original_bind_pose=arguments.guess_original_bind_pose,
        disable_bone_shape=arguments.disable_bone_shape,
    )


@dataclasses.dataclass
class ExportSceneGltfArguments:
    filepath: str
    check_existing: bool
    export_format: str
    export_extras: bool
    export_def_bones: bool
    export_current_frame: bool
    use_selection: bool
    use_active_scene: bool
    export_animations: bool
    export_armature_object_remove: bool
    export_rest_position_armature: bool
    export_all_influences: bool
    export_vertex_color: str
    export_lights: bool
    export_try_sparse_sk: bool
    export_apply: bool


def __invoke_export_scene_gltf(arguments: ExportSceneGltfArguments) -> set[str]:
    if bpy.app.version < (3, 2):
        return bpy.ops.export_scene.gltf(
            filepath=arguments.filepath,
            check_existing=arguments.check_existing,
            export_format=arguments.export_format,
            export_extras=arguments.export_extras,
            export_def_bones=False,
            export_current_frame=arguments.export_current_frame,
            use_selection=arguments.use_selection,
            export_animations=arguments.export_animations,
            export_all_influences=arguments.export_all_influences,
            export_lights=arguments.export_lights,
            export_apply=arguments.export_apply,
        )

    if bpy.app.version < (3, 6):
        return bpy.ops.export_scene.gltf(
            filepath=arguments.filepath,
            check_existing=arguments.check_existing,
            export_format=arguments.export_format,
            export_extras=arguments.export_extras,
            export_def_bones=(bpy.app.version >= (3, 3)) and arguments.export_def_bones,
            export_current_frame=arguments.export_current_frame,
            use_selection=arguments.use_selection,
            use_active_scene=arguments.use_active_scene,
            export_animations=arguments.export_animations,
            export_all_influences=arguments.export_all_influences,
            export_lights=arguments.export_lights,
            export_apply=arguments.export_apply,
        )

    if bpy.app.version < (4,):
        return bpy.ops.export_scene.gltf(
            filepath=arguments.filepath,
            check_existing=arguments.check_existing,
            export_format=arguments.export_format,
            export_extras=arguments.export_extras,
            export_def_bones=arguments.export_def_bones,
            export_current_frame=arguments.export_current_frame,
            use_selection=arguments.use_selection,
            use_active_scene=arguments.use_active_scene,
            export_animations=arguments.export_animations,
            export_rest_position_armature=arguments.export_rest_position_armature,
            export_all_influences=arguments.export_all_influences,
            export_lights=arguments.export_lights,
            export_apply=arguments.export_apply,
        )

    if bpy.app.version < (4, 2):
        return bpy.ops.export_scene.gltf(
            filepath=arguments.filepath,
            check_existing=arguments.check_existing,
            export_format=arguments.export_format,
            export_extras=arguments.export_extras,
            export_def_bones=arguments.export_def_bones,
            export_current_frame=arguments.export_current_frame,
            use_selection=arguments.use_selection,
            use_active_scene=arguments.use_active_scene,
            export_animations=arguments.export_animations,
            export_rest_position_armature=arguments.export_rest_position_armature,
            export_try_sparse_sk=arguments.export_try_sparse_sk,
            export_all_influences=arguments.export_all_influences,
            export_lights=arguments.export_lights,
            export_apply=arguments.export_apply,
        )

    return bpy.ops.export_scene.gltf(
        filepath=arguments.filepath,
        check_existing=arguments.check_existing,
        export_format=arguments.export_format,
        export_extras=arguments.export_extras,
        export_def_bones=arguments.export_def_bones,
        export_current_frame=arguments.export_current_frame,
        use_selection=arguments.use_selection,
        use_active_scene=arguments.use_active_scene,
        export_animations=arguments.export_animations,
        export_armature_object_remove=arguments.export_armature_object_remove,
        export_rest_position_armature=arguments.export_rest_position_armature,
        export_vertex_color=arguments.export_vertex_color,
        export_try_sparse_sk=arguments.export_try_sparse_sk,
        export_all_influences=arguments.export_all_influences,
        export_lights=arguments.export_lights,
        export_apply=arguments.export_apply,
    )


def export_scene_gltf(arguments: ExportSceneGltfArguments) -> set[str]:
    try:
        return __invoke_export_scene_gltf(arguments)
    except RuntimeError:
        if not arguments.export_animations:
            raise
        logger.exception("Failed to export VRM with animations")
        # TODO: check traceback

    arguments.export_animations = False
    return __invoke_export_scene_gltf(arguments)


def gather_gltf2_io_material(
    material: Material, export_settings: dict[str, object]
) -> Optional[gltf2_io.Material]:
    if bpy.app.version < (3, 2):
        from io_scene_gltf2.blender.exp.gltf2_blender_gather_materials import (
            gather_material as gather_material_before_3_2,
        )

        return gather_material_before_3_2(material, export_settings)

    if bpy.app.version < (3, 6):
        from io_scene_gltf2.blender.exp.gltf2_blender_gather_materials import (
            gather_material as gather_material_before_3_6,
        )

        return gather_material_before_3_6(material, 0, export_settings)

    if bpy.app.version < (4, 0):
        from io_scene_gltf2.blender.exp.material.gltf2_blender_gather_materials import (
            gather_material as gather_material_before_4_0,
        )

        return gather_material_before_4_0(material, 0, export_settings)

    if bpy.app.version < (4, 3):
        from io_scene_gltf2.blender.exp.material.gltf2_blender_gather_materials import (
            gather_material as gather_material_before_4_3,
        )

        gltf2_io_material, _ = gather_material_before_4_3(material, export_settings)
        return gltf2_io_material

    from io_scene_gltf2.blender.exp.material.materials import gather_material

    gltf2_io_material, _ = gather_material(material, export_settings)
    return gltf2_io_material
