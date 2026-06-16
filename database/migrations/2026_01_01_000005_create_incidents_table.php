<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class () extends Migration {
    public function up(): void
    {
        Schema::create('incidents', function (Blueprint $table) {
            $table->id();
            $table->foreignId('event_id')->constrained()->cascadeOnDelete();
            $table->string('reference');
            $table->string('location');
            $table->string('priority', 10);
            $table->string('category', 50);
            $table->text('description');
            $table->string('status', 20)->default('new');
            $table->timestamps();

            $table->unique(['event_id', 'reference']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('incidents');
    }
};
