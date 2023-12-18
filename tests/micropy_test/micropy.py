import lvgl as lv
import ubinascii
import fs_driver
import time


try:
    lv.log_register_print_cb  # NOQA

    raise RuntimeError('Logging in LVGL MUST be disabled to run the tests.')
except AttributeError:
    pass


if not lv.is_initialized():
    lv.init()


fs_drv = lv.fs_drv_t()
fs_driver.fs_register(fs_drv, 'A')


WIDTH = 800
HEIGHT = 480


def flush(disp, area, color_p):
    x1 = area.x1
    x2 = area.x2
    y1 = area.y1
    y2 = area.y2

    size = (x2 - x1 + 1) * (y2 - y1 + 1) * lv.color_format_get_size(disp.get_color_format())
    data_view = color_p.__dereference__(size)
    byte_count = 0

    print('FRAME START')

    while byte_count != size:
        chunk_size = min(size - byte_count, 512)
        chunk = data_view[byte_count:chunk_size + byte_count]
        byte_count += chunk_size
        print(ubinascii.hexlify(bytes(chunk)).decode('utf-8'))

    print('FRAME END')
    disp.flush_ready()


disp_drv = lv.display_create(WIDTH, HEIGHT)
disp_drv.set_flush_cb(flush)
disp_drv.set_color_format(lv.COLOR_FORMAT.RGB888)

color_size = lv.color_format_get_size(disp_drv.get_color_format())

buf = bytearray(WIDTH * HEIGHT * color_size)
disp_drv.set_draw_buffers(buf, None, WIDTH * HEIGHT * color_size, lv.DISPLAY_RENDER_MODE.FULL)


def GRID_FR(x):
    return lv.COORD.MAX - 100 + x


def CANVAS_BUF_SIZE(w, h, bpp, stride):
    return ((((w * bpp + 7) >> 3) + stride - 1) & ~(stride - 1)) * h + lv.DRAW_BUF_ALIGN


def create_ui():
    # Create a colors
    c1 = lv.color_hex(0xff0000)
    c2 = lv.palette_darken(lv.PALETTE.BLUE, 2)
    c3 = c1.mix(c2, lv.OPA._60)

    # Create a style
    style_big_font = lv.style_t()
    style_big_font.init()

    # Use a built-in font
    style_big_font.set_text_font(lv.font_montserrat_24)

    # Get the active screen
    scr = lv.screen_active()

    # Declare static array of integers, and test grid setting options
    gird_cols = [300, GRID_FR(3), GRID_FR(2), lv.GRID_TEMPLATE_LAST]
    gird_rows = [100, GRID_FR(1), lv.GRID_CONTENT, lv.GRID_TEMPLATE_LAST]
    scr.set_grid_dsc_array(gird_cols, gird_rows)

    chart_type_subject = lv.subject_t()
    chart_type_subject.init_int(0)

    # Create a widget
    dropdown = lv.dropdown(scr)

    # Pass a string as argument
    dropdown.set_options("Lines\nBars")

    # Use grid align options
    dropdown.set_grid_cell(lv.GRID_ALIGN.CENTER, 0, 1, lv.GRID_ALIGN.CENTER, 0, 1)

    # Bind to a subject
    dropdown.bind_value(chart_type_subject)

    # Create a chart with an external array of points
    chart = lv.chart(lv.screen_active())
    chart.set_grid_cell(lv.GRID_ALIGN.STRETCH, 0, 1, lv.GRID_ALIGN.CENTER, 1, 1)

    series = chart.add_series(c3, lv.chart.AXIS.PRIMARY_X)

    chart_y_array = [10, 25, 50, 40, 30, 35, 60, 65, 70, 75]

    chart.set_ext_y_array(series, chart_y_array)

    # Add custom observer callback
    chart_type_subject.add_observer_obj(lambda _, __: chart_type_observer_cb(chart, chart_type_subject), chart, None)

    # Manually set the subject's value
    chart_type_subject.set_int(1)

    label = lv.label(scr)
    label.set_grid_cell(lv.GRID_ALIGN.START, 1, 1, lv.GRID_ALIGN.CENTER, 0, 1)

    # Apply styles on main part and default state
    label.set_style_bg_opa(lv.OPA._70, 0)
    label.set_style_bg_color(c1, 0)
    label.set_style_text_color(c2, 0)
    label.add_style(style_big_font, 0)

    # Declare an array of strings
    btnmatrix_options = [
        "First", "Second", "\n",
        "Third", ""
    ]

    btnmatrix_ctrl = [
        lv.buttonmatrix.CTRL.DISABLED, 2 | lv.buttonmatrix.CTRL.CHECKED,
        1,
    ]

    btnmatrix = lv.buttonmatrix(scr)
    btnmatrix.set_grid_cell(lv.GRID_ALIGN.STRETCH, 1, 1, lv.GRID_ALIGN.STRETCH, 1, 1)
    # Pass string and enum arrays
    btnmatrix.set_map(btnmatrix_options)
    btnmatrix.set_ctrl_map(btnmatrix_ctrl)
    # Add style to non main part and non default state
    btnmatrix.add_style(style_big_font, lv.PART.ITEMS | lv.STATE.CHECKED)

    btnmatrix.set_selected_button(1)
    btnmatrix.add_event_cb(lambda _: buttonmatrix_event_cb(btnmatrix, label), lv.EVENT.VALUE_CHANGED, None)
    btnmatrix.send_event(lv.EVENT.VALUE_CHANGED, None)

    # Create a base object
    cont = lv.obj(scr)
    # Span 2 rows
    cont.set_grid_cell(lv.GRID_ALIGN.STRETCH, 2, 1, lv.GRID_ALIGN.STRETCH, 0, 2)

    # Apply flex layout
    cont.set_flex_flow(lv.FLEX_FLOW.COLUMN)

    btn1 = list_button_create(cont)
    btn2 = list_button_create(cont)
    btn3 = list_button_create(cont)
    btn4 = list_button_create(cont)
    btn5 = list_button_create(cont)
    btn6 = list_button_create(cont)
    btn7 = list_button_create(cont)
    btn8 = list_button_create(cont)
    btn9 = list_button_create(cont)
    btn10 = list_button_create(cont)

    a = lv.anim_t()
    a.init()
    a.set_var(btn1)
    a.set_values(lv.OPA.COVER, lv.OPA._50)
    a.set_custom_exec_cb(lambda _, v: opa_anim_cb(btn1, v))  # Pass a callback
    a.set_time(300)
    a.set_path_cb(lv.anim_t.path_ease_out)
    a.start()

    btn2.add_flag(lv.obj.FLAG.HIDDEN)

    btn_label = btn3.get_child(0)
    btn_label.set_text("A multi-line text with a ° symbol")
    btn_label.set_width(lv.pct(100))

    a = lv.anim_t()
    a.init()
    a.set_var(btn4)
    a.set_values(lv.OPA.COVER, lv.OPA._50)
    a.set_custom_exec_cb(lambda _, v: opa_anim_cb(btn4, v))  # Pass a callback
    a.set_path_cb(lv.anim_t.path_ease_out)
    a.set_time(300)
    a.set_repeat_count(lv.ANIM_REPEAT_INFINITE)
    a.start()

    # Wait and delete the button with the animation

    cont.get_child(3).delete()
    # Large byte array

    canvas_buf = bytearray(CANVAS_BUF_SIZE(400, 100, 16, 1))

    canvas = lv.canvas(scr)
    canvas.set_grid_cell(lv.GRID_ALIGN.START, 0, 2, lv.GRID_ALIGN.START, 2, 1)
    # Test RGB565 rendering
    canvas.set_buffer(lv.draw_buf_align(canvas_buf, lv.COLOR_FORMAT.RGB565), 400, 100, lv.COLOR_FORMAT.RGB565)
    canvas.fill_bg(c2, lv.OPA.COVER)
    draw_to_canvas(canvas)

    test_img_lvgl_logo_jpg_data = bytes(bytearray([
        0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46, 0x00, 0x01, 0x01,
        0x01, 0x01, 0x2c, 0x01, 0x2c, 0x00, 0x00, 0xff, 0xfe, 0x00, 0x13, 0x43, 0x72,
        0x65, 0x61, 0x74, 0x65, 0x64, 0x20, 0x77, 0x69, 0x74, 0x68, 0x20, 0x47, 0x49,
        0x4d, 0x50, 0xff, 0xdb, 0x00, 0x43, 0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05,
        0x08, 0x07, 0x07, 0x07, 0x09, 0x09, 0x08, 0x0a, 0x0c, 0x15, 0x0e, 0x0c, 0x0b,
        0x0b, 0x0c, 0x19, 0x12, 0x13, 0x0f, 0x15, 0x1e, 0x1b, 0x20, 0x1f, 0x1e, 0x1b,
        0x1d, 0x1d, 0x21, 0x25, 0x30, 0x29, 0x21, 0x23, 0x2d, 0x24, 0x1d, 0x1d, 0x2a,
        0x39, 0x2a, 0x2d, 0x31, 0x33, 0x36, 0x36, 0x36, 0x20, 0x28, 0x3b, 0x3f, 0x3a,
        0x34, 0x3e, 0x30, 0x35, 0x36, 0x33, 0xff, 0xdb, 0x00, 0x43, 0x01, 0x09, 0x09,
        0x09, 0x0c, 0x0b, 0x0c, 0x18, 0x0e, 0x0e, 0x18, 0x33, 0x22, 0x1d, 0x22, 0x33,
        0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33,
        0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33,
        0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33,
        0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0xff, 0xc0, 0x00,
        0x11, 0x08, 0x00, 0x21, 0x00, 0x69, 0x03, 0x01, 0x11, 0x00, 0x02, 0x11, 0x01,
        0x03, 0x11, 0x01, 0xff, 0xc4, 0x00, 0x1f, 0x00, 0x00, 0x01, 0x05, 0x01, 0x01,
        0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
        0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0xff, 0xc4, 0x00,
        0xb5, 0x10, 0x00, 0x02, 0x01, 0x03, 0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04,
        0x04, 0x00, 0x00, 0x01, 0x7d, 0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12,
        0x21, 0x31, 0x41, 0x06, 0x13, 0x51, 0x61, 0x07, 0x22, 0x71, 0x14, 0x32, 0x81,
        0x91, 0xa1, 0x08, 0x23, 0x42, 0xb1, 0xc1, 0x15, 0x52, 0xd1, 0xf0, 0x24, 0x33,
        0x62, 0x72, 0x82, 0x09, 0x0a, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x25, 0x26, 0x27,
        0x28, 0x29, 0x2a, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x43, 0x44, 0x45,
        0x46, 0x47, 0x48, 0x49, 0x4a, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5a,
        0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6a, 0x73, 0x74, 0x75, 0x76, 0x77,
        0x78, 0x79, 0x7a, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8a, 0x92, 0x93,
        0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9a, 0xa2, 0xa3, 0xa4, 0xa5, 0xa6, 0xa7,
        0xa8, 0xa9, 0xaa, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0xc2,
        0xc3, 0xc4, 0xc5, 0xc6, 0xc7, 0xc8, 0xc9, 0xca, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6,
        0xd7, 0xd8, 0xd9, 0xda, 0xe1, 0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9,
        0xea, 0xf1, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6, 0xf7, 0xf8, 0xf9, 0xfa, 0xff, 0xc4,
        0x00, 0x1f, 0x01, 0x00, 0x03, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06,
        0x07, 0x08, 0x09, 0x0a, 0x0b, 0xff, 0xc4, 0x00, 0xb5, 0x11, 0x00, 0x02, 0x01,
        0x02, 0x04, 0x04, 0x03, 0x04, 0x07, 0x05, 0x04, 0x04, 0x00, 0x01, 0x02, 0x77,
        0x00, 0x01, 0x02, 0x03, 0x11, 0x04, 0x05, 0x21, 0x31, 0x06, 0x12, 0x41, 0x51,
        0x07, 0x61, 0x71, 0x13, 0x22, 0x32, 0x81, 0x08, 0x14, 0x42, 0x91, 0xa1, 0xb1,
        0xc1, 0x09, 0x23, 0x33, 0x52, 0xf0, 0x15, 0x62, 0x72, 0xd1, 0x0a, 0x16, 0x24,
        0x34, 0xe1, 0x25, 0xf1, 0x17, 0x18, 0x19, 0x1a, 0x26, 0x27, 0x28, 0x29, 0x2a,
        0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49,
        0x4a, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5a, 0x63, 0x64, 0x65, 0x66,
        0x67, 0x68, 0x69, 0x6a, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79, 0x7a, 0x82,
        0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8a, 0x92, 0x93, 0x94, 0x95, 0x96,
        0x97, 0x98, 0x99, 0x9a, 0xa2, 0xa3, 0xa4, 0xa5, 0xa6, 0xa7, 0xa8, 0xa9, 0xaa,
        0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0xc2, 0xc3, 0xc4, 0xc5,
        0xc6, 0xc7, 0xc8, 0xc9, 0xca, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7, 0xd8, 0xd9,
        0xda, 0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9, 0xea, 0xf2, 0xf3, 0xf4,
        0xf5, 0xf6, 0xf7, 0xf8, 0xf9, 0xfa, 0xff, 0xda, 0x00, 0x0c, 0x03, 0x01, 0x00,
        0x02, 0x11, 0x03, 0x11, 0x00, 0x3f, 0x00, 0x4f, 0x11, 0xfc, 0x6b, 0xf1, 0x25,
        0x8f, 0x89, 0x35, 0x2b, 0x2b, 0x2b, 0x7b, 0x04, 0xb7, 0xb6, 0xb9, 0x78, 0x50,
        0x49, 0x13, 0x33, 0x10, 0xac, 0x57, 0x24, 0xee, 0x1d, 0x71, 0x9a, 0x00, 0xcb,
        0xff, 0x00, 0x85, 0xeb, 0xe2, 0xef, 0xf9, 0xe7, 0xa6, 0xff, 0x00, 0xdf, 0x86,
        0xff, 0x00, 0xe2, 0xa9, 0x88, 0xd7, 0xf0, 0xe7, 0xc5, 0x5f, 0x1b, 0xf8, 0x9b,
        0x57, 0x5d, 0x36, 0xd6, 0x4d, 0x0e, 0x09, 0x59, 0x19, 0xc3, 0xdc, 0xc6, 0xc8,
        0xb8, 0x03, 0x3d, 0x77, 0x1e, 0x69, 0x0c, 0xf5, 0x4f, 0x87, 0xfe, 0x25, 0xbb,
        0xf1, 0x4f, 0x84, 0xe3, 0xd4, 0x6f, 0xa3, 0x85, 0x2e, 0x44, 0xaf, 0x14, 0x9e,
        0x47, 0xdc, 0x62, 0xa7, 0x19, 0x1c, 0x9a, 0x00, 0xd7, 0xd0, 0xb5, 0xbb, 0x5f,
        0x11, 0x69, 0x11, 0x6a, 0x56, 0x42, 0x41, 0x04, 0x8c, 0xca, 0xa2, 0x45, 0xc3,
        0x65, 0x58, 0xa9, 0xe3, 0xea, 0x0d, 0x00, 0x26, 0xb9, 0xae, 0xda, 0x78, 0x7a,
        0xce, 0x2b, 0xbb, 0xe1, 0x20, 0xb7, 0x79, 0xd2, 0x16, 0x91, 0x14, 0x11, 0x19,
        0x63, 0x80, 0xcd, 0xcf, 0x0b, 0x9c, 0x73, 0xef, 0x40, 0x1a, 0x74, 0x01, 0x43,
        0x5a, 0xd6, 0x2d, 0x34, 0x0d, 0x22, 0xe3, 0x53, 0xbe, 0x66, 0x10, 0x42, 0x01,
        0x21, 0x46, 0x59, 0x89, 0x38, 0x00, 0x0e, 0xe4, 0x92, 0x00, 0x14, 0x00, 0xeb,
        0xcd, 0x56, 0xcf, 0x4d, 0xd3, 0x0e, 0xa3, 0xa8, 0xce, 0xb6, 0x76, 0xea, 0xa1,
        0x9d, 0xa7, 0x21, 0x76, 0xe7, 0xb1, 0xf7, 0xf6, 0x14, 0x01, 0xce, 0xaf, 0xc4,
        0x0b, 0x69, 0xd7, 0xcd, 0xb4, 0xd0, 0x7c, 0x43, 0x75, 0x6d, 0xd4, 0x5c, 0x45,
        0xa7, 0xb6, 0xc2, 0x3d, 0x40, 0x24, 0x12, 0x3e, 0x82, 0x80, 0x36, 0xb4, 0x4f,
        0x11, 0xe9, 0x7e, 0x21, 0x8a, 0x47, 0xd3, 0xee, 0x0b, 0x3c, 0x27, 0x6c, 0xd0,
        0xc8, 0x86, 0x39, 0x62, 0x3e, 0x8c, 0x8d, 0x82, 0x28, 0x01, 0xe9, 0xad, 0xda,
        0xc9, 0xe2, 0x29, 0xb4, 0x35, 0x12, 0x7d, 0xae, 0x2b, 0x65, 0xb9, 0x63, 0xb7,
        0xe5, 0xd8, 0x58, 0xa8, 0xe7, 0xd7, 0x20, 0xd0, 0x06, 0x95, 0x00, 0x14, 0x01,
        0xf3, 0x87, 0x88, 0x6f, 0x3c, 0x26, 0x3c, 0x49, 0xaa, 0x09, 0xfc, 0x20, 0x25,
        0x98, 0x5d, 0xca, 0x1e, 0x4f, 0xed, 0x29, 0x57, 0x7b, 0x6f, 0x39, 0x38, 0x1c,
        0x0c, 0x9e, 0x71, 0x5c, 0x13, 0xc6, 0xb8, 0xc9, 0xab, 0x6c, 0x7d, 0x66, 0x1f,
        0x86, 0x63, 0x56, 0x94, 0x6a, 0x7b, 0x4b, 0x5d, 0x27, 0xb7, 0x75, 0xea, 0x72,
        0x3e, 0x3c, 0xd2, 0xac, 0xb4, 0x5f, 0x18, 0xde, 0xd8, 0xe9, 0xd1, 0x34, 0x56,
        0x88, 0x23, 0x68, 0xe3, 0x67, 0x2d, 0xb7, 0x74, 0x6a, 0xc4, 0x64, 0xf2, 0x79,
        0x26, 0xbb, 0xd3, 0xba, 0x3e, 0x52, 0x4b, 0x96, 0x4d, 0x1c, 0xe5, 0x32, 0x4f,
        0xa6, 0x7e, 0x09, 0x7f, 0xc9, 0x37, 0x8f, 0xfe, 0xbe, 0x65, 0xfe, 0x62, 0x90,
        0xcd, 0x4f, 0x85, 0x5f, 0xf2, 0x4f, 0x6c, 0x7f, 0xeb, 0xb4, 0xff, 0x00, 0xfa,
        0x39, 0xe8, 0x03, 0xa4, 0xd6, 0xb4, 0xab, 0x7d, 0x73, 0x44, 0xbc, 0xd2, 0xee,
        0x86, 0x61, 0xba, 0x89, 0xa3, 0x6f, 0x6c, 0xf4, 0x23, 0xdc, 0x1c, 0x1f, 0xc2,
        0x80, 0x31, 0xbc, 0x05, 0xaa, 0xdc, 0x6a, 0x1e, 0x1c, 0x16, 0x97, 0xe7, 0xfe,
        0x26, 0x7a, 0x64, 0x8d, 0x65, 0x76, 0x0f, 0x52, 0xe9, 0xc0, 0x6f, 0xf8, 0x12,
        0xe0, 0xfe, 0x34, 0x01, 0x4f, 0x5c, 0xff, 0x00, 0x8a, 0x8b, 0xc7, 0x3a, 0x66,
        0x82, 0xbf, 0x35, 0x9e, 0x98, 0x06, 0xa1, 0x7d, 0xe8, 0x5f, 0xa4, 0x28, 0x7f,
        0x1c, 0xb6, 0x3d, 0x85, 0x00, 0x45, 0x35, 0xb4, 0x7e, 0x27, 0xf8, 0x9f, 0x3d,
        0xb5, 0xe8, 0x12, 0xd8, 0xe8, 0x16, 0xf1, 0x49, 0x1d, 0xbb, 0x0c, 0xab, 0x5c,
        0x49, 0x92, 0x1c, 0x8e, 0xfb, 0x54, 0x71, 0xe8, 0x4d, 0x00, 0x77, 0x34, 0x01,
        0x02, 0x2d, 0xaa, 0xde, 0x4a, 0xd1, 0xac, 0x22, 0xe5, 0x95, 0x7c, 0xd2, 0xb8,
        0xde, 0x40, 0xe9, 0x9e, 0xf8, 0xe4, 0xe2, 0x80, 0x39, 0x3b, 0x5f, 0xf9, 0x2c,
        0x7a, 0x87, 0xfd, 0x81, 0x61, 0xff, 0x00, 0xd1, 0xad, 0x40, 0x1d, 0x9d, 0x00,
        0x14, 0x01, 0xf3, 0xc6, 0xbd, 0xff, 0x00, 0x08, 0x5f, 0xfc, 0x24, 0x5a, 0x9f,
        0xda, 0x06, 0xbf, 0xe7, 0xfd, 0xae, 0x5f, 0x33, 0xcb, 0x30, 0xed, 0xdd, 0xbc,
        0xe7, 0x19, 0xe7, 0x19, 0xaf, 0x26, 0xa7, 0xb1, 0xe7, 0x77, 0xbf, 0xe0, 0x7e,
        0x87, 0x83, 0xfe, 0xd2, 0xfa, 0xbd, 0x3e, 0x4e, 0x4b, 0x59, 0x5a, 0xfc, 0xd7,
        0xb5, 0x89, 0xbc, 0x79, 0x61, 0xe0, 0xc9, 0xbc, 0x5d, 0x73, 0x26, 0xa0, 0x75,
        0xe1, 0x72, 0x63, 0x8b, 0x7f, 0xd9, 0xcc, 0x3b, 0x31, 0xe5, 0xae, 0x31, 0xbb,
        0x9e, 0x98, 0xcf, 0xbd, 0x76, 0x4f, 0x15, 0x0a, 0x6f, 0x95, 0xa3, 0xe6, 0xb0,
        0xd9, 0x0e, 0x23, 0x17, 0x4f, 0xdb, 0x46, 0x49, 0x27, 0x7e, 0xfd, 0xfd, 0x0e,
        0x1b, 0xc6, 0x7a, 0x06, 0x9d, 0xa1, 0x5d, 0x69, 0xad, 0xa5, 0xcd, 0x75, 0x25,
        0xa5, 0xf5, 0x92, 0xdc, 0xa8, 0xba, 0xdb, 0xbd, 0x72, 0xcc, 0x30, 0x76, 0xf1,
        0xfc, 0x35, 0xd3, 0x09, 0x29, 0xc5, 0x49, 0x1e, 0x3e, 0x26, 0x84, 0xb0, 0xf5,
        0x65, 0x4a, 0x5b, 0xa7, 0x63, 0xdc, 0xfe, 0x09, 0x7f, 0xc9, 0x37, 0x8f, 0xfe,
        0xbe, 0x65, 0xfe, 0x62, 0x99, 0x89, 0xa1, 0xf0, 0xb2, 0x68, 0x93, 0xe1, 0xfd,
        0x92, 0xb4, 0xa8, 0x0f, 0x9d, 0x3f, 0x05, 0x87, 0xfc, 0xf6, 0x7a, 0x00, 0xed,
        0x16, 0x68, 0x9d, 0xb6, 0xac, 0x88, 0xc7, 0xd0, 0x30, 0x34, 0x01, 0xc2, 0x6b,
        0x97, 0x90, 0x78, 0x27, 0xc7, 0x2b, 0xae, 0x5c, 0x37, 0x95, 0xa4, 0xeb, 0x10,
        0x18, 0x6e, 0xdb, 0xb2, 0x4f, 0x1a, 0x96, 0x46, 0xfa, 0xb2, 0x82, 0xbf, 0x80,
        0xa0, 0x0d, 0x3f, 0x00, 0xd9, 0x4e, 0x34, 0x79, 0xb5, 0xbb, 0xf4, 0x2b, 0xa8,
        0x6b, 0x33, 0x1b, 0xb9, 0x41, 0xea, 0x88, 0x78, 0x8d, 0x3f, 0xe0, 0x29, 0x8f,
        0xcc, 0xd0, 0x05, 0x1d, 0x66, 0x56, 0xf0, 0x87, 0x8d, 0x9b, 0xc4, 0x73, 0x46,
        0xcd, 0xa3, 0x6a, 0x50, 0x25, 0xbd, 0xf4, 0xa8, 0xa5, 0x8d, 0xbc, 0x88, 0x4e,
        0xc9, 0x1b, 0x1f, 0xc2, 0x41, 0x20, 0x9e, 0xd4, 0x01, 0xd8, 0x5b, 0x6a, 0x36,
        0x37, 0x96, 0xcb, 0x73, 0x6d, 0x79, 0x04, 0xd0, 0x30, 0xc8, 0x92, 0x39, 0x03,
        0x29, 0x1f, 0x51, 0x40, 0x1c, 0x96, 0x83, 0x79, 0x6d, 0xa8, 0x7c, 0x4d, 0xf1,
        0x0d, 0xc5, 0x9c, 0xf1, 0xdc, 0x40, 0x96, 0x56, 0xd1, 0x34, 0x91, 0x36, 0xe5,
        0x0e, 0x0b, 0xe5, 0x72, 0x38, 0xc8, 0xc8, 0xe2, 0x80, 0x16, 0x09, 0x12, 0x3f,
        0x8c, 0x5a, 0x81, 0x77, 0x55, 0x1f, 0xd8, 0xb0, 0xf5, 0x38, 0xff, 0x00, 0x96,
        0xad, 0x40, 0x1d, 0x8f, 0xda, 0x20, 0xff, 0x00, 0x9e, 0xd1, 0xff, 0x00, 0xdf,
        0x42, 0x80, 0x1d, 0xbd, 0x3f, 0xbe, 0xbf, 0x9d, 0x00, 0x79, 0x46, 0xa9, 0xf0,
        0x6a, 0x6d, 0x47, 0x56, 0xbc, 0xbd, 0x1a, 0xda, 0x20, 0xb8, 0x9d, 0xe5, 0x08,
        0x6d, 0x89, 0xdb, 0xb9, 0x89, 0xc6, 0x77, 0x7b, 0xd7, 0x04, 0xf0, 0x5c, 0xd2,
        0x6f, 0x98, 0xfa, 0xcc, 0x3f, 0x13, 0x46, 0x95, 0x28, 0xd3, 0xf6, 0x57, 0xb2,
        0x4b, 0x7e, 0xcb, 0xd0, 0xb7, 0xe2, 0x3f, 0x84, 0xd2, 0xeb, 0xda, 0xdc, 0xba,
        0x82, 0xeb, 0x09, 0x08, 0x91, 0x11, 0x76, 0x1b, 0x72, 0xd8, 0xda, 0x81, 0x7a,
        0xee, 0xf6, 0xaa, 0xab, 0x84, 0xe7, 0x97, 0x35, 0xcc, 0x70, 0x3c, 0x42, 0xb0,
        0xb4, 0x15, 0x2f, 0x67, 0x7b, 0x5f, 0xaf, 0x77, 0x7e, 0xc5, 0x4f, 0x12, 0x7c,
        0x1a, 0x97, 0x5e, 0x8f, 0x49, 0x55, 0xd6, 0xd2, 0x13, 0x61, 0x64, 0xb6, 0xa4,
        0x9b, 0x62, 0xdb, 0xf0, 0xcc, 0x77, 0x7d, 0xee, 0x3e, 0xf7, 0x4a, 0xea, 0xa7,
        0x1e, 0x48, 0xa8, 0xf6, 0x3c, 0x1c, 0x5d, 0x7f, 0xac, 0x57, 0x9d, 0x5b, 0x5b,
        0x99, 0xdc, 0xee, 0x3c, 0x15, 0xe1, 0x64, 0xf0, 0x7f, 0x86, 0x61, 0xd2, 0x16,
        0xe4, 0xdc, 0x95, 0x66, 0x77, 0x94, 0xae, 0xdd, 0xc5, 0x8f, 0x61, 0x93, 0x81,
        0x56, 0x73, 0x91, 0x37, 0xc3, 0xcf, 0x08, 0x33, 0x16, 0x6f, 0x0f, 0x58, 0x12,
        0x4e, 0x49, 0x31, 0x75, 0xa0, 0x0b, 0x7a, 0x6f, 0x83, 0xfc, 0x3b, 0xa3, 0xde,
        0xad, 0xe6, 0x9d, 0xa3, 0xda, 0x5a, 0xdc, 0xa8, 0x20, 0x49, 0x12, 0x60, 0x80,
        0x7a, 0xd0, 0x05, 0xfd, 0x4f, 0x4a, 0xb0, 0xd6, 0x6c, 0xcd, 0xa6, 0xa5, 0x69,
        0x15, 0xd5, 0xb9, 0x60, 0xc6, 0x39, 0x57, 0x23, 0x23, 0xa1, 0xa0, 0x0b, 0x6a,
        0xa1, 0x54, 0x2a, 0x80, 0x00, 0x18, 0x00, 0x76, 0xa0, 0x01, 0x95, 0x5d, 0x4a,
        0xb2, 0x86, 0x52, 0x30, 0x41, 0x19, 0x06, 0x80, 0x39, 0xb9, 0xbe, 0x1e, 0xf8,
        0x42, 0x79, 0xcc, 0xd2, 0x78, 0x7a, 0xc3, 0x79, 0x39, 0x38, 0x88, 0x00, 0x4f,
        0xd0, 0x71, 0x40, 0x1b, 0xb6, 0x56, 0x16, 0x9a, 0x6d, 0xaa, 0xdb, 0x58, 0xda,
        0xc3, 0x6d, 0x02, 0x7d, 0xd8, 0xe1, 0x40, 0x8a, 0x3f, 0x01, 0x40, 0x19, 0xda,
        0xa7, 0x84, 0xbc, 0x3f, 0xad, 0xdd, 0x8b, 0xbd, 0x4f, 0x49, 0xb5, 0xbb, 0xb8,
        0x0a, 0x10, 0x49, 0x2a, 0x64, 0xed, 0x1d, 0x07, 0xea, 0x68, 0x02, 0x8f, 0xfc,
        0x2b, 0xbf, 0x07, 0xff, 0x00, 0xd0, 0xbb, 0x61, 0xff, 0x00, 0x7e, 0xa8, 0x03,
        0x73, 0xfb, 0x32, 0xcb, 0xfe, 0x7d, 0xd2, 0x80, 0x2d, 0xd0, 0x01, 0x40, 0x05,
        0x00, 0x14, 0x00, 0x50, 0x01, 0x40, 0x05, 0x00, 0x14, 0x00, 0x50, 0x01, 0x40,
        0x05, 0x00, 0x14, 0x00, 0x50, 0x01, 0x40, 0x1f, 0xff, 0xd9
    ]))

    test_img_lvgl_logo_jpg = lv.image_dsc_t(
        dict(
            header=dict(cf=lv.COLOR_FORMAT.RAW_ALPHA, w=105, h=33),
            data_size=1947,
            data=test_img_lvgl_logo_jpg_data
        )
    )

    img = lv.image(scr)
    img.set_src(test_img_lvgl_logo_jpg)
    img.align(lv.ALIGN.BOTTOM_RIGHT, -20, -20)
    img.add_flag(lv.obj.FLAG.IGNORE_LAYOUT)

    img = lv.image(scr)
    img.set_src("A:test_img_lvgl_logo.png")
    img.set_pos(500, 420)
    img.add_flag(lv.obj.FLAG.IGNORE_LAYOUT)
    img.set_rotation(200)
    img.set_scale_x(400)


def chart_type_observer_cb(chart, subject):
    v = subject.get_int()
    # chart = observer.get_target()
    chart.set_type(lv.chart.TYPE.LINE if v == 0 else lv.chart.TYPE.BAR)


def buttonmatrix_event_cb(buttonmatrix, label):
    # label = e.get_user_data()
    # buttonmatrix = e.get_target()
    idx = buttonmatrix.get_selected_button()
    text = buttonmatrix.get_button_text(idx)
    label.set_text(text)


def list_button_create(parent):
    btn = lv.button(parent)
    btn.set_size(lv.pct(100), lv.SIZE_CONTENT)

    # Get an integer
    idx = btn.get_index()

    # Formatted string for label
    label = lv.label(btn)
    label.set_text(lv.SYMBOL.FILE + " Item %d" % idx)

    return btn


def opa_anim_cb(button, value):
    try:
        button.set_style_opa(value, 0)
    except:  # NOQA
        pass


def draw_to_canvas(canvas):
    layer = lv.layer_t()
    canvas.init_layer(layer)

    # Use draw descriptors

    test_img_lvgl_logo_png_data = bytes(bytearray([
        0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d, 0x49,
        0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x69, 0x00, 0x00, 0x00, 0x21, 0x08, 0x06,
        0x00, 0x00, 0x00, 0xda, 0x89, 0x85, 0x3b, 0x00, 0x00, 0x00, 0x06, 0x62, 0x4b,
        0x47, 0x44, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xf9, 0x43, 0xbb, 0x7f, 0x00,
        0x00, 0x00, 0x09, 0x70, 0x48, 0x59, 0x73, 0x00, 0x00, 0x2e, 0x23, 0x00, 0x00,
        0x2e, 0x23, 0x01, 0x78, 0xa5, 0x3f, 0x76, 0x00, 0x00, 0x00, 0x07, 0x74, 0x49,
        0x4d, 0x45, 0x07, 0xe7, 0x09, 0x12, 0x12, 0x25, 0x07, 0x59, 0xa0, 0x4e, 0xa5,
        0x00, 0x00, 0x00, 0x19, 0x74, 0x45, 0x58, 0x74, 0x43, 0x6f, 0x6d, 0x6d, 0x65,
        0x6e, 0x74, 0x00, 0x43, 0x72, 0x65, 0x61, 0x74, 0x65, 0x64, 0x20, 0x77, 0x69,
        0x74, 0x68, 0x20, 0x47, 0x49, 0x4d, 0x50, 0x57, 0x81, 0x0e, 0x17, 0x00, 0x00,
        0x06, 0xb9, 0x49, 0x44, 0x41, 0x54, 0x68, 0xde, 0xed, 0x9a, 0x7f, 0x8c, 0x5d,
        0x45, 0x15, 0xc7, 0x3f, 0xe7, 0xbe, 0xf7, 0x76, 0xa9, 0x20, 0x18, 0x03, 0x9a,
        0x6a, 0x77, 0xe6, 0xdd, 0xb7, 0x6b, 0x8a, 0x49, 0xc3, 0x1a, 0xb5, 0x25, 0x80,
        0xb5, 0xe2, 0x6a, 0x2b, 0x0d, 0x46, 0x71, 0x89, 0x8a, 0xbf, 0x48, 0x4c, 0xd5,
        0xd4, 0x46, 0x08, 0x58, 0x48, 0x10, 0xc5, 0xe8, 0x3f, 0xa6, 0x68, 0x6b, 0xe4,
        0x0f, 0x85, 0x22, 0x68, 0x53, 0x6d, 0x9a, 0x40, 0x31, 0x40, 0xc0, 0x92, 0xb6,
        0xd0, 0x62, 0x53, 0x4a, 0xac, 0x44, 0xa2, 0xad, 0xa4, 0x76, 0xf7, 0xde, 0xb9,
        0xaf, 0x3f, 0x0c, 0x0a, 0xd2, 0x96, 0x6d, 0xd9, 0xdd, 0xb7, 0xf7, 0xf8, 0xc7,
        0x9b, 0xca, 0x76, 0xf7, 0xfd, 0x5c, 0x77, 0xdd, 0xd7, 0xe4, 0x7d, 0x93, 0x97,
        0x97, 0xb9, 0x33, 0x77, 0x66, 0xce, 0xf9, 0xce, 0x39, 0x73, 0xe6, 0xcc, 0x85,
        0x36, 0xda, 0x68, 0xe3, 0x7f, 0x87, 0x00, 0x98, 0x7c, 0xbe, 0x13, 0x95, 0xe5,
        0x40, 0x0f, 0x5a, 0x7e, 0x36, 0x8d, 0x23, 0x0c, 0xa1, 0x6c, 0x4d, 0x92, 0x68,
        0xa0, 0xad, 0xee, 0x29, 0xaa, 0xd0, 0x5a, 0x13, 0x28, 0x99, 0xcd, 0xc0, 0xf5,
        0x67, 0x48, 0x9b, 0x01, 0x9c, 0x00, 0x96, 0x26, 0x2e, 0x7a, 0xbe, 0xad, 0xf2,
        0xe6, 0x91, 0x85, 0xcc, 0x42, 0xa0, 0x7f, 0x06, 0x08, 0x2a, 0x01, 0x81, 0xff,
        0x5d, 0x08, 0xdc, 0x02, 0x7c, 0x7e, 0x7c, 0x83, 0xae, 0xae, 0x82, 0x48, 0xa0,
        0x9d, 0x80, 0x04, 0xa2, 0xc3, 0x71, 0x1c, 0xa7, 0xf5, 0x3a, 0x35, 0xb6, 0x90,
        0x45, 0x35, 0x07, 0x68, 0x92, 0x44, 0x6f, 0x4c, 0x75, 0x72, 0xf3, 0xc2, 0x30,
        0x08, 0x52, 0x3a, 0x01, 0x4d, 0x5c, 0xfd, 0x7e, 0xac, 0x0d, 0x73, 0xaa, 0xbc,
        0x05, 0xd1, 0x9c, 0x57, 0xd5, 0x88, 0xa2, 0xa7, 0x8b, 0x2e, 0x1e, 0x6d, 0x64,
        0x3c, 0x6b, 0x0b, 0x19, 0x55, 0xed, 0x40, 0x34, 0x4d, 0x5c, 0x3c, 0xdc, 0xcc,
        0x5c, 0x03, 0x85, 0x8b, 0xbd, 0x22, 0xa7, 0x13, 0x03, 0xc0, 0xe5, 0xc0, 0xa7,
        0x80, 0xd3, 0xfe, 0xd9, 0x3b, 0x27, 0x99, 0xb1, 0xf0, 0x56, 0xe0, 0x79, 0xe0,
        0x40, 0xaa, 0xd2, 0xdb, 0x58, 0xd7, 0xda, 0x8b, 0xb0, 0x1f, 0xe1, 0xaf, 0xc6,
        0x86, 0xf3, 0xa7, 0xec, 0x42, 0x52, 0xbe, 0x08, 0xbc, 0x04, 0x3c, 0x62, 0xf2,
        0x85, 0x6c, 0x45, 0x22, 0x4d, 0x3e, 0x6b, 0x6c, 0xf8, 0x31, 0x63, 0xc3, 0x5f,
        0x2b, 0xbc, 0x88, 0x30, 0x08, 0x52, 0x04, 0x8a, 0xc0, 0xa0, 0x20, 0x7f, 0x36,
        0x36, 0x7c, 0xc0, 0xd8, 0x70, 0x89, 0xc9, 0x87, 0x99, 0x9a, 0xb3, 0x46, 0xaf,
        0x43, 0x78, 0x09, 0xe4, 0x31, 0x63, 0xc3, 0x6c, 0x53, 0x24, 0xcd, 0x90, 0x85,
        0x3e, 0x9b, 0xb8, 0xe8, 0x05, 0xa1, 0xf4, 0x24, 0x70, 0xac, 0xce, 0xf8, 0xef,
        0x06, 0x8c, 0x22, 0xb9, 0x86, 0x28, 0x4a, 0xf5, 0x45, 0xe0, 0x35, 0xa0, 0x1b,
        0x58, 0x31, 0x95, 0xc9, 0x19, 0x53, 0xc8, 0x08, 0x7c, 0x0b, 0x30, 0xc0, 0x13,
        0x49, 0x3c, 0x58, 0x9a, 0x68, 0xe1, 0xc6, 0x86, 0x57, 0x07, 0x22, 0x7b, 0x80,
        0x6d, 0xc0, 0x8d, 0xc0, 0x7c, 0x20, 0x07, 0xfc, 0xc3, 0xcb, 0x94, 0xf5, 0xcf,
        0xbe, 0x0a, 0xec, 0x44, 0x79, 0xda, 0xd8, 0xb0, 0xd6, 0x42, 0x9b, 0xe3, 0xc7,
        0x9b, 0xab, 0xa2, 0xb4, 0x02, 0x49, 0xfd, 0xc6, 0x86, 0xb7, 0x2b, 0xd9, 0xb5,
        0x80, 0x9d, 0xce, 0x8e, 0x8b, 0xc5, 0xb8, 0x04, 0xfc, 0xd8, 0x17, 0x57, 0xd8,
        0x7c, 0x78, 0x49, 0xb3, 0x7d, 0xa8, 0x68, 0x1f, 0xb0, 0x10, 0x38, 0x26, 0xe8,
        0x86, 0xb3, 0x09, 0xcc, 0x8b, 0x04, 0x7a, 0x07, 0xf0, 0xd4, 0x99, 0x36, 0xc0,
        0xf7, 0x80, 0x45, 0x88, 0xbe, 0x23, 0x71, 0x51, 0x98, 0xb8, 0xa8, 0xa0, 0xa2,
        0x97, 0x80, 0xf6, 0x02, 0xb7, 0x01, 0x09, 0xf0, 0x61, 0xe0, 0x59, 0x63, 0xc3,
        0x65, 0x33, 0xb0, 0x27, 0xcd, 0x08, 0x2e, 0x04, 0xd6, 0xcc, 0xd8, 0x4e, 0xaa,
        0x3c, 0x86, 0x10, 0x03, 0x79, 0x55, 0xbe, 0x0c, 0xac, 0x6b, 0xf4, 0x55, 0x6b,
        0xc3, 0x40, 0xe1, 0x26, 0x5f, 0x7c, 0xd0, 0xb9, 0xf8, 0xf5, 0x71, 0xfb, 0x94,
        0x90, 0xf2, 0x5d, 0xe0, 0x87, 0x80, 0x02, 0xbf, 0x50, 0xe1, 0x8e, 0x62, 0x1c,
        0x1d, 0x9f, 0xb4, 0x58, 0xe2, 0x78, 0x14, 0xd8, 0x0f, 0xec, 0x37, 0xa6, 0x70,
        0x1f, 0xa2, 0x6b, 0x80, 0x65, 0x40, 0x34, 0xdd, 0xe2, 0x06, 0xc0, 0xcb, 0x40,
        0xca, 0x39, 0x84, 0x24, 0x89, 0x86, 0x80, 0xfb, 0x7d, 0x71, 0xa5, 0xb5, 0xb6,
        0xa3, 0x71, 0x7e, 0xb9, 0xd4, 0x2b, 0xf3, 0x34, 0x70, 0xef, 0x59, 0xca, 0x48,
        0xe9, 0x03, 0xee, 0xf2, 0xc5, 0xef, 0xa8, 0xe8, 0xaa, 0x4a, 0x04, 0x4d, 0x9e,
        0xcf, 0xe0, 0x49, 0x90, 0x55, 0x22, 0xb2, 0x30, 0x71, 0xd1, 0xc1, 0x69, 0xb7,
        0xa4, 0x4c, 0x90, 0xee, 0x2b, 0x8d, 0x05, 0xbd, 0x12, 0xc8, 0xdc, 0x2a, 0x62,
        0x65, 0x51, 0xbe, 0x06, 0x5c, 0xd7, 0x4a, 0x44, 0xa9, 0x72, 0x9f, 0x08, 0xab,
        0x81, 0x1e, 0x25, 0xb8, 0x1e, 0xd8, 0xd4, 0xe0, 0xab, 0xab, 0xbd, 0x07, 0xd9,
        0x90, 0xb8, 0xe8, 0xf0, 0x9b, 0x51, 0xa3, 0xed, 0x04, 0xd6, 0xfa, 0xba, 0x8d,
        0x28, 0x6b, 0x8a, 0x2e, 0x6e, 0x78, 0xf3, 0x48, 0xdc, 0xa0, 0x02, 0xaf, 0xce,
        0x48, 0x08, 0xbe, 0x35, 0x72, 0x73, 0xb4, 0x1c, 0x89, 0x9d, 0x57, 0x79, 0xe1,
        0xf1, 0xf8, 0x52, 0x1b, 0xfe, 0xc0, 0x47, 0x6a, 0x41, 0xab, 0x90, 0x54, 0x4c,
        0xa2, 0x57, 0x8c, 0x0d, 0x37, 0x03, 0x2b, 0x81, 0x6f, 0x74, 0xf7, 0xbc, 0x67,
        0xf3, 0xc0, 0xa1, 0xbf, 0xa7, 0xb5, 0xc3, 0xf7, 0xf0, 0x5d, 0xfe, 0xb8, 0x51,
        0x9a, 0x68, 0x45, 0x10, 0x7c, 0x04, 0xb8, 0x0c, 0x18, 0x42, 0xb9, 0x33, 0x49,
        0x22, 0x6d, 0x15, 0x59, 0xb3, 0x0a, 0x4b, 0x80, 0x5f, 0xd6, 0x68, 0x93, 0x57,
        0xd8, 0x20, 0x65, 0xc2, 0x5a, 0x0d, 0x3f, 0xf5, 0x11, 0xde, 0xe2, 0xd1, 0x91,
        0xd2, 0x95, 0xc0, 0xee, 0x3a, 0xed, 0xbf, 0xee, 0xf7, 0xcb, 0xa7, 0x12, 0x17,
        0xed, 0x9b, 0x50, 0xf7, 0x05, 0xff, 0xff, 0x50, 0x92, 0x44, 0xc5, 0x56, 0x12,
        0x32, 0x68, 0xc0, 0x3a, 0x02, 0x5a, 0x15, 0x2a, 0x87, 0x80, 0x47, 0x01, 0x41,
        0xb8, 0x79, 0x5e, 0x97, 0x91, 0x1a, 0x01, 0xc3, 0x45, 0x9e, 0xa4, 0x14, 0xf8,
        0xd9, 0xf8, 0xba, 0x8b, 0xbb, 0x17, 0x08, 0xb0, 0xc8, 0x17, 0x9f, 0x6e, 0x35,
        0x31, 0x5b, 0x97, 0x80, 0x86, 0x02, 0x88, 0x41, 0x05, 0x7e, 0xee, 0xdd, 0xf2,
        0xb5, 0x22, 0xd9, 0x7c, 0x8d, 0x80, 0xa1, 0x1f, 0x98, 0x0b, 0xfc, 0x2d, 0x95,
        0x74, 0xfb, 0xf8, 0xba, 0xf3, 0x4b, 0xa7, 0x2e, 0xa0, 0x7c, 0xa8, 0x4f, 0x81,
        0x43, 0x6d, 0x92, 0xa6, 0x19, 0x63, 0xa3, 0x23, 0x3b, 0x81, 0xe7, 0x80, 0xf3,
        0x44, 0xf4, 0x96, 0x4a, 0x6d, 0xba, 0x0a, 0x61, 0xce, 0x07, 0x0c, 0x00, 0x6b,
        0x0f, 0xc7, 0xee, 0xac, 0x54, 0x4e, 0x0a, 0x19, 0xaf, 0x0b, 0x05, 0x86, 0xa7,
        0x32, 0x0f, 0x63, 0xc3, 0x15, 0xc6, 0x86, 0x1b, 0x8d, 0x0d, 0xfb, 0xdb, 0x24,
        0x4d, 0xc0, 0x91, 0xa3, 0x47, 0xc6, 0x5b, 0xd3, 0x0d, 0xc6, 0x16, 0xde, 0x3e,
        0x29, 0x05, 0x34, 0xc6, 0x32, 0x9f, 0x1d, 0x38, 0x2a, 0x2a, 0x5b, 0x26, 0xd6,
        0x67, 0x44, 0x87, 0x81, 0x51, 0xaf, 0x8f, 0x8b, 0xa6, 0x38, 0x95, 0xcb, 0x81,
        0x2f, 0xf9, 0xe0, 0xa3, 0x4d, 0xd2, 0x24, 0x12, 0x08, 0xb6, 0x00, 0xae, 0xec,
        0xb2, 0xf4, 0xc6, 0x0a, 0x4d, 0x6e, 0xf2, 0xb2, 0xae, 0x77, 0xc9, 0xe0, 0x89,
        0x89, 0x95, 0x71, 0x1c, 0x9d, 0xf6, 0xef, 0x0b, 0xb0, 0xa0, 0x15, 0xdd, 0x5d,
        0xbd, 0x2c, 0xee, 0x28, 0xc2, 0x49, 0x60, 0xa4, 0x55, 0x49, 0x72, 0x6e, 0xe0,
        0x8d, 0x71, 0xc1, 0xc0, 0x2a, 0x6b, 0xed, 0x9c, 0x71, 0x6e, 0x68, 0x11, 0xf0,
        0x51, 0xe0, 0x84, 0x0a, 0xeb, 0x6b, 0x74, 0xf3, 0x8c, 0xff, 0xff, 0x4c, 0xab,
        0xc9, 0x97, 0x55, 0x78, 0x46, 0xe0, 0x9a, 0x2a, 0xe7, 0xa4, 0x14, 0xf8, 0x83,
        0xa0, 0xaf, 0x81, 0x5c, 0xa1, 0x10, 0x56, 0x5e, 0xc9, 0x04, 0x94, 0xef, 0xa3,
        0x6e, 0x98, 0xc5, 0x48, 0x6f, 0x13, 0xa2, 0xdf, 0x07, 0x0a, 0x4a, 0x70, 0x0d,
        0xf0, 0xc8, 0x99, 0x8c, 0x04, 0xe5, 0x3d, 0x67, 0x4b, 0x31, 0x8e, 0x8e, 0xd5,
        0x48, 0x45, 0xfc, 0x06, 0xe1, 0x56, 0x60, 0xb1, 0xb1, 0xe1, 0x92, 0xc4, 0x45,
        0xbb, 0x5a, 0x86, 0xa4, 0x71, 0x7e, 0x78, 0x4e, 0x25, 0x92, 0x14, 0x3a, 0xb6,
        0xc7, 0x71, 0x90, 0x96, 0x09, 0x7a, 0x5b, 0x95, 0x03, 0xef, 0xae, 0x3e, 0xd3,
        0xbd, 0x2b, 0x23, 0x69, 0x3f, 0xd0, 0x31, 0x1b, 0x82, 0x24, 0xc9, 0xe0, 0xcb,
        0xc6, 0x86, 0x0f, 0x00, 0xdf, 0x06, 0x6e, 0xeb, 0xe9, 0x9e, 0xff, 0xbb, 0xe1,
        0xd2, 0x48, 0x17, 0xe5, 0x3b, 0xac, 0x12, 0xf0, 0x93, 0x9a, 0x2e, 0x25, 0xe0,
        0x40, 0xaa, 0x3c, 0x01, 0x7c, 0x1a, 0xb8, 0xa7, 0xcb, 0x14, 0x16, 0x17, 0x2b,
        0xb8, 0xc6, 0x59, 0x21, 0x49, 0xe0, 0x6a, 0x60, 0x73, 0x75, 0x7f, 0xcf, 0xdd,
        0x29, 0xfc, 0x0a, 0x78, 0xd8, 0xaf, 0xc8, 0x4a, 0xd8, 0x74, 0xa4, 0x23, 0xb3,
        0xd2, 0x8c, 0xa6, 0xb3, 0x9b, 0x03, 0x54, 0xd6, 0x23, 0x7c, 0x13, 0x58, 0x38,
        0x52, 0x1a, 0xb9, 0x4a, 0xe0, 0x5a, 0xef, 0x21, 0x9e, 0x94, 0xf2, 0xdd, 0x51,
        0x55, 0xc4, 0x71, 0x94, 0x5a, 0x1b, 0xde, 0xac, 0x70, 0x25, 0x70, 0x99, 0x88,
        0x3e, 0x64, 0x6c, 0xfe, 0xb3, 0x89, 0x8b, 0x8f, 0xcf, 0x36, 0x49, 0x41, 0x0d,
        0xc5, 0xbf, 0x19, 0xfc, 0xd4, 0x6f, 0x93, 0x6d, 0x85, 0x15, 0x97, 0x24, 0xd1,
        0x41, 0x60, 0xab, 0x97, 0xe9, 0x76, 0xe0, 0x2b, 0xbe, 0xea, 0x1e, 0xe7, 0xa2,
        0xba, 0x0b, 0xc8, 0xb9, 0x28, 0x01, 0x3e, 0x07, 0x9c, 0x04, 0x96, 0x82, 0x3c,
        0x67, 0x6c, 0xd8, 0x67, 0x4c, 0x4f, 0xa6, 0x7a, 0xe8, 0x5d, 0x08, 0x8c, 0x0d,
        0xdf, 0x0f, 0x7c, 0x68, 0x26, 0xdd, 0x5d, 0x4b, 0x04, 0x68, 0x82, 0x5e, 0x65,
        0x6c, 0xbe, 0xd1, 0xbb, 0xa1, 0xe3, 0x89, 0x8b, 0x77, 0x57, 0xb1, 0xfc, 0x35,
        0x5a, 0xce, 0x33, 0x7e, 0xd2, 0x3f, 0xda, 0x97, 0xcb, 0xe5, 0xb6, 0x37, 0x4c,
        0xb4, 0x8b, 0x76, 0x1a, 0x1b, 0x2e, 0x05, 0x7e, 0x0b, 0xbc, 0x17, 0xd8, 0x86,
        0x8c, 0xed, 0x35, 0x36, 0xfc, 0x3d, 0xc8, 0x1f, 0x11, 0x2d, 0xa2, 0xaa, 0xa8,
        0xcc, 0x45, 0x78, 0x1f, 0xe8, 0xc7, 0x81, 0x3e, 0xaf, 0xcb, 0x18, 0x78, 0xbc,
        0xce, 0x10, 0x17, 0x88, 0xb2, 0xdc, 0xd8, 0xfc, 0x58, 0x63, 0xce, 0x41, 0x0e,
        0xb4, 0x0c, 0x49, 0xc0, 0xba, 0x26, 0x3e, 0xb3, 0x78, 0x01, 0xf8, 0x40, 0x15,
        0xa9, 0xfe, 0x84, 0xb0, 0x97, 0xb2, 0xdb, 0x02, 0xb8, 0x77, 0xe0, 0xd0, 0xc1,
        0xb1, 0xa6, 0x2c, 0xd2, 0x45, 0x7b, 0x4d, 0x3e, 0xfc, 0x20, 0xca, 0x6a, 0x9f,
        0x4a, 0xba, 0xa2, 0xfc, 0x53, 0x9f, 0xc1, 0x94, 0x89, 0x53, 0xfd, 0x27, 0x70,
        0xbf, 0x90, 0xae, 0x73, 0xce, 0xbd, 0x52, 0xa7, 0xfb, 0x10, 0xe4, 0xd1, 0x26,
        0x14, 0x73, 0x6b, 0x76, 0x76, 0xcd, 0x27, 0x1d, 0x51, 0x64, 0x23, 0x70, 0x7e,
        0x93, 0xaf, 0x56, 0x4d, 0x80, 0xba, 0x24, 0x2a, 0x19, 0x1b, 0xde, 0xe5, 0xdd,
        0x56, 0x49, 0x48, 0x37, 0x4d, 0xc9, 0x75, 0xc6, 0xd1, 0xbf, 0x81, 0x3b, 0x8d,
        0xc9, 0xff, 0x08, 0x91, 0x4f, 0x78, 0xa2, 0x7a, 0x7c, 0x90, 0x75, 0xe6, 0x5a,
        0x62, 0x00, 0xd8, 0x13, 0x08, 0xdb, 0xe2, 0x38, 0x1a, 0xaa, 0x63, 0x12, 0x03,
        0xc8, 0x7f, 0xef, 0xc0, 0x9a, 0x59, 0xbd, 0x7f, 0xf9, 0x7f, 0x92, 0x94, 0x4c,
        0xde, 0x03, 0xe2, 0x53, 0x94, 0xbf, 0x22, 0x9a, 0xde, 0x81, 0x5c, 0xb4, 0x03,
        0xd8, 0x31, 0x3d, 0xfb, 0x5c, 0xfc, 0xba, 0x0f, 0x9a, 0x1e, 0x9e, 0x37, 0x2f,
        0x94, 0x20, 0x53, 0x3e, 0x99, 0x24, 0xce, 0x69, 0x73, 0xfd, 0x44, 0x7b, 0x80,
        0x3d, 0x53, 0xdd, 0x93, 0x4a, 0xf5, 0xd2, 0x63, 0x0a, 0xf5, 0xdc, 0x45, 0x89,
        0x52, 0xa9, 0x04, 0x0c, 0x55, 0x39, 0x6f, 0x1d, 0x05, 0xee, 0x3e, 0xd7, 0x33,
        0x1b, 0x87, 0x0f, 0xcf, 0xce, 0x1d, 0x93, 0x1c, 0x84, 0xce, 0xb4, 0xbc, 0xc9,
        0x76, 0x56, 0x39, 0x03, 0xed, 0x50, 0xf8, 0x97, 0xc0, 0x72, 0xca, 0x77, 0x31,
        0x95, 0xb0, 0xfb, 0x52, 0x70, 0xc6, 0xe4, 0x7b, 0x09, 0x64, 0xc1, 0x84, 0x1e,
        0x4e, 0x29, 0xec, 0x2a, 0xba, 0xe8, 0x55, 0xda, 0x68, 0xa3, 0x8d, 0x36, 0xda,
        0x68, 0xa3, 0x8d, 0x73, 0x1a, 0xff, 0x01, 0xc1, 0xba, 0x4f, 0x53, 0x6b, 0xda,
        0x6f, 0x58, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60,
        0x82
    ]))

    test_img_lvgl_logo_png = lv.image_dsc_t(
        dict(
            header=dict(cf=lv.COLOR_FORMAT.RAW_ALPHA, w=105, h=33),
            data_size=1873,
            data=test_img_lvgl_logo_png_data
        )
    )

    image_draw_dsc = lv.draw_image_dsc_t()

    image_draw_dsc.init()
    image_draw_dsc.src = test_img_lvgl_logo_png

    coords = lv.area_t(dict(x1=10, y1=10, x2=10 + test_img_lvgl_logo_png.header.w - 1, y2=10 + test_img_lvgl_logo_png.header.h - 1))
    lv.draw_image(layer, image_draw_dsc, coords)

    # Reuse the draw descriptor
    coords.move(40, 40)
    image_draw_dsc.opa = lv.OPA._50
    lv.draw_image(layer, image_draw_dsc, coords)

    line_draw_dsc = lv.draw_line_dsc_t()
    line_draw_dsc.init()
    line_draw_dsc.color = lv.color_hex3(0xCA8)
    line_draw_dsc.width = 8
    line_draw_dsc.round_end = 1
    line_draw_dsc.round_start = 1
    line_draw_dsc.p1.x = 150
    line_draw_dsc.p1.y = 30
    line_draw_dsc.p2.x = 350
    line_draw_dsc.p2.y = 55
    lv.draw_line(layer, line_draw_dsc)

    canvas.finish_layer(layer)

    c = lv.color_hex(0xff0000)
    for i in range(50):
        canvas.set_px(100 + i * 2, 10, c, lv.OPA.COVER)


create_ui()

start_time = time.time_ns()

left_over = 0
while True:
    curr_time = time.time_ns()
    new_amount = time.ticks_diff(start_time, curr_time) + left_over
    new_amount = abs(new_amount)
    left_over = new_amount & 0x3E8
    new_amount >>= 12
    new_amount = abs(new_amount)
    
    if new_amount:
        lv.tick_inc(new_amount)
        lv.task_handler()
        start_time = curr_time

# end
